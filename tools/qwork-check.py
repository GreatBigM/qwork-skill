#!/usr/bin/env python3
"""qwork 变更门：检查 change 目录是否可派发（dispatch）或可收口（close）。

用法:
  python3 tools/qwork-check.py <change-dir> --dispatch [--strict] [--json]
  python3 tools/qwork-check.py <change-dir> --close    [--strict] [--json]

退出码: 0 = 通过；1 = 有 error（--strict 下 warning 也算失败）。
无外部依赖；只读，不改任何文件（git cat-file 只读）。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

S_ID = re.compile(r"^S\d+$")
C_ID = re.compile(r"^C\d+$")
STATUS_LINE = re.compile(r"^\s*-\s+\[( |x|X|!)\]\s+(.*)$")
BLOCKED_HINT = re.compile(r"(BLOCKED_[A-Z0-9_]+|阻塞原因\s*[:：]|等待|无法继续)", re.I)
UNVERIFIED = re.compile(r"(未验证|待验证|未完成|待补)", re.I)
PLACEHOLDER = re.compile(r"<[^>]+>")
FENCE = re.compile(r"^\s*(```|~~~)")
HASH = re.compile(r"^[0-9a-fA-F]{7,40}$")
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
NUMERIC = re.compile(r"([-+]?\d+(?:\.\d+)?)\s*([A-Za-z%℃]+)?")

HANDOFF_FIELDS = ("必读", "环境", "禁止", "决策权", "启动条件", "停止", "判据", "回报", "交付")
VERDICTS = ("✅", "❌", "⚠️")


class Findings:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.verdicts = {"pass": 0, "fail": 0, "blocked": 0}
        self.rejected = False

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def ok(self, strict: bool) -> bool:
        return not self.errors and not (strict and self.warnings)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, *keywords: str) -> str | None:
    lines = text.splitlines()
    start = None
    level = 2
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,2})\s+(.*)$", line)
        if m:
            heading = m.group(2).strip()
            if any(heading == k or heading.startswith(k + " ") or heading.startswith(k + "（") for k in keywords):
                start = i + 1
                level = len(m.group(1))
                break
    if start is None:
        return None
    out: list[str] = []
    for line in lines[start:]:
        m = re.match(r"^(#{1,2})\s+", line)
        if m and len(m.group(1)) <= level:
            break
        out.append(line)
    return "\n".join(out)


def split_row(line: str) -> list[str]:
    """按 | 切表格行，保留 \\| 转义。"""
    tmp = line.strip().replace("\\|", "\x00")
    if tmp.startswith("|"):
        tmp = tmp[1:]
    if tmp.endswith("|"):
        tmp = tmp[:-1]
    return [c.replace("\x00", "|").strip() for c in tmp.split("|")]


def tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    found: list[tuple[list[str], list[list[str]]]] = []
    header: list[str] | None = None
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if header is not None and rows:
                found.append((header, rows))
            header, rows = None, []
            continue
        cells = split_row(stripped)
        if all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in cells if c):
            continue
        if header is None:
            header = cells
        else:
            rows.append(cells)
    if header is not None and rows:
        found.append((header, rows))
    return found


def find_table(text: str | None, required: tuple[str, ...]) -> tuple[list[str], list[list[str]]] | None:
    if text is None:
        return None
    for header, rows in tables(text):
        norm = [h.lower() for h in header]
        if all(any(r.lower() in h for h in norm) for r in required):
            return header, rows
    return None


def column(header: list[str], *names: str) -> int | None:
    for i, h in enumerate(header):
        if any(n.lower() in h.lower() for n in names):
            return i
    return None


def cell(row: list[str], idx: int | None) -> str:
    if idx is None or idx >= len(row):
        return ""
    return row[idx].strip()


def is_retroactive(spec_text: str) -> bool:
    for line in spec_text.splitlines()[:30]:
        if re.match(r"^\s*>\s*retroactive\b", line, re.I):
            return True
    return False


def parse_verdict(raw: str) -> tuple[str | None, str]:
    text = raw.strip()
    for symbol in VERDICTS:
        if text.startswith(symbol):
            return symbol, text[len(symbol):].strip()
    return None, text


def normalized_unit(unit: str | None) -> str:
    if not unit:
        return ""
    u = unit.lower()
    return {"分钟": "min", "分": "min", "秒": "s", "毫秒": "ms"}.get(u, u)


def numeric_compare(target: str, actual: str) -> bool | None:
    """返回 True=满足，False=违反，None=无法机械比较。只处理简单数值。"""
    t = re.sub(r"^S\d+\s*[:：]\s*", "", target.strip())
    if any(x in t for x in ("基线", "×", "*", "包络")):
        return None
    m = re.fullmatch(r"(≤|≥|<|>|=)\s*([-+]?\d+(?:\.\d+)?)\s*([A-Za-z%℃]+)?", t)
    if not m:
        return None
    op, tval, tunit = m.group(1), float(m.group(2)), normalized_unit(m.group(3))
    a = re.fullmatch(r"[≈~]?\s*([-+]?\d+(?:\.\d+)?)\s*([A-Za-z%℃]+)?", actual.strip())
    if not a:
        return None
    aval, aunit = float(a.group(1)), normalized_unit(a.group(2))
    if tunit and aunit and tunit != aunit:
        return None
    if op == "≤":
        return aval <= tval
    if op == "≥":
        return aval >= tval
    if op == "<":
        return aval < tval
    if op == ">":
        return aval > tval
    return abs(aval - tval) < 1e-9


def project_root(change: Path) -> Path | None:
    parts = change.resolve().parts
    if "0_workbench" in parts:
        idx = parts.index("0_workbench")
        return Path(*parts[:idx])
    return None


def check_evidence(desc: str, change: Path, root: Path | None, f: Findings) -> None:
    if "→" not in desc:
        f.error(f"任务完成但缺证据（需 → commit <hash> / → 证据: <path> / → 用户确认: <who> <date> <ref>）：{desc[:60]}")
        return
    ev = desc.rsplit("→", 1)[1].strip().strip("`").strip()
    if not ev or ("<" in ev and ">" in ev):
        f.error(f"任务证据为空或仍是占位符：{desc[:60]}")
        return

    if ev.startswith("用户确认") or ev.startswith("确认:") or ev.startswith("确认："):
        if DATE.search(ev):
            return
        f.error(f"用户确认证据缺日期（YYYY-MM-DD）：{desc[:60]}")
        return

    if ev.startswith("证据:") or ev.startswith("证据："):
        content = ev.split(":", 1)[1] if ":" in ev else ev.split("：", 1)[1]
        content = content.strip().strip("`").strip()
        if not content:
            f.error(f"证据路径为空：{desc[:60]}")
            return
        if "用户确认" in content or "确认无需" in content:
            if DATE.search(content):
                return
            f.error(f"证据里写用户确认但缺日期（YYYY-MM-DD）：{desc[:60]}")
            return
        path_token = content.split()[0].strip("`，。;；")
        candidates = [Path(path_token)] if Path(path_token).is_absolute() else []
        candidates += [change / path_token, root / path_token] if root else [change / path_token]
        existing = [p for p in candidates if p.is_file()]
        if any(p.stat().st_size > 0 for p in existing):
            return
        if existing:
            f.error(f"证据文件为空：{path_token}（任务：{desc[:60]}）")
            return
        f.error(f"证据路径不存在：{path_token}（任务：{desc[:60]}）")
        return

    raw_hash = ev[len("commit"):].strip() if ev.lower().startswith("commit") else ev
    if HASH.fullmatch(raw_hash):
        if root is None:
            f.error(f"commit 证据无法校验（找不到 0_workbench 项目根）：{raw_hash}")
            return
        p = subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{raw_hash}^{{commit}}"],
                           text=True, capture_output=True)
        if p.returncode != 0:
            f.error(f"commit 证据不存在或不可解析：{raw_hash}")
        return

    f.error(f"无法识别的证据（需 commit hash / 证据路径 / 用户确认）：{ev[:80]}")


def check_spec(change: Path, f: Findings, legacy: bool) -> dict[str, str] | None:
    path = change / "spec.md"
    if not path.is_file():
        f.error("spec.md 缺失")
        return None
    text = read(path)
    sec = section(text, "成功标准", "要什么")
    if sec is None:
        f.error("spec.md 缺少「要什么（成功标准）」小节")
        return None
    tab = find_table(sec, ("ID", "基线", "目标"))
    if tab is None:
        legacy_tab = find_table(sec, ("维度", "基线", "目标"))
        if legacy_tab is not None and legacy:
            f.warn("legacy（retroactive）：成功标准表无 ID 列，跳过 S/C 追踪检查")
            return None
        if legacy_tab is not None:
            f.error("spec 成功标准表缺少 ID 列；新 change 请用模板，存量先标 > retroactive: <日期> <原因>")
        else:
            f.error("spec.md 成功标准表缺少 ID/基线/目标 列")
        return None
    header, rows = tab
    id_i = column(header, "ID")
    base_i = column(header, "基线")
    target_i = column(header, "目标")
    ids: dict[str, str] = {}
    for row in rows:
        sid = cell(row, id_i)
        if not S_ID.match(sid):
            f.error(f"spec 行 ID 非法：{sid!r}（应为 S1、S2...）")
            continue
        if sid in ids:
            f.error(f"spec ID 重复：{sid}")
        if not cell(row, base_i) or not cell(row, target_i):
            f.error(f"spec {sid} 缺基线或目标")
        ids[sid] = cell(row, target_i)
    if not ids:
        f.error("spec 成功标准表没有有效数据行")
    return ids or None


def check_check(change: Path, spec_ids: dict[str, str] | None, f: Findings, legacy: bool) -> dict[str, str] | None:
    path = change / "check.md"
    if not path.is_file():
        f.error("check.md 缺失")
        return None
    text = read(path)
    sec = section(text, "验收项", "验收方法", "验收")
    tab = find_table(sec, ("ID", "spec", "判定"))
    if tab is None:
        if legacy:
            f.warn("legacy（retroactive）：check 无 ID/spec/判定 表，跳过 C 追踪检查")
        else:
            f.error("check 验收表缺少 ID/spec/判定 列；新 change 请用模板，存量先标 > retroactive")
        return None
    header, rows = tab
    id_i = column(header, "ID")
    spec_i = column(header, "spec")
    method_i = column(header, "检查方法", "方法", "命令")
    verdict_i = column(header, "判定")
    type_i = column(header, "类型")
    ids: dict[str, str] = {}
    for row in rows:
        cid = cell(row, id_i)
        ref = cell(row, spec_i)
        if not C_ID.match(cid):
            f.error(f"check 行 ID 非法：{cid!r}（应为 C1、C2...）")
            continue
        if cid in ids:
            f.error(f"check ID 重复：{cid}")
        if spec_ids is not None and ref not in spec_ids:
            f.error(f"check {cid} 引用了不存在的 spec「{ref}」")
        method = cell(row, method_i)
        if not method:
            f.error(f"check {cid} 缺检查方法")
        elif PLACEHOLDER.search(method):
            f.error(f"check {cid} 检查方法仍是占位符：{method[:60]}")
        if verdict_i is not None and not cell(row, verdict_i):
            f.error(f"check {cid} 缺判定口径")
        if type_i is not None:
            typ = cell(row, type_i)
            if typ and typ not in ("自动", "人工"):
                f.error(f"check {cid} 类型必须是「自动」或「人工」（当前 {typ!r}）")
        ids[cid] = ref
    if not ids:
        f.error("check 验收表没有有效数据行")
    if spec_ids:
        used = set(ids.values())
        for sid in spec_ids:
            if sid not in used:
                f.error(f"spec {sid} 没有任何 check 项覆盖")
    return ids or None


def check_handoff(tasks: str, f: Findings, legacy: bool) -> None:
    sec = section(tasks, "接手须知")
    if sec is None:
        msg = "tasks 缺少「接手须知」（新 change 必须填全 9 项）"
        if legacy:
            f.warn("legacy（retroactive）：" + msg)
        else:
            f.error(msg)
        return
    for kw in HANDOFF_FIELDS:
        if kw not in sec:
            f.error(f"接手须知缺少「{kw}」")


def check_closure(tasks: str, mode: str, legacy: bool, f: Findings) -> None:
    """tasks 是执行唯一台账：收口段（design 吸收 / 项目 spec / 产出沉淀）全勾才算完结。"""
    sec = section(tasks, "收口")
    if sec is None:
        msg = "tasks 缺少「收口」段（design 吸收 / 项目 spec 复审 / 产出沉淀；全勾才算完结）"
        if not legacy:
            f.error(msg)
        else:
            f.warn(msg)
        return
    states = task_states(sec)
    if not states:
        msg = "tasks「收口」段没有任务复选框"
        if not legacy:
            f.error(msg)
        else:
            f.warn(msg)
        return
    if mode == "close":
        unchecked = [d for s, d in states if s == " "]
        if unchecked:
            f.error(f"tasks 收口段仍有 {len(unchecked)} 项未完成（[ ]）")


def task_states(tasks: str) -> list[tuple[str, str]]:
    states: list[tuple[str, str]] = []
    in_fence = False
    for line in tasks.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = STATUS_LINE.match(line)
        if m:
            states.append((m.group(1), m.group(2)))
    return states


def has_rejection(spec_text: str, design_text: str, tasks: str) -> bool:
    top = "\n".join(spec_text.splitlines()[:20])
    marker = "⚠️" in top and "证伪" in top and re.search(r"状态\s*[:：]\s*拒绝", top) is not None
    return marker and "证伪记录" in design_text and "最终" in tasks and "❌" in tasks and "未通过" in tasks


def has_blocked_closure(spec_text: str, tasks: str) -> bool:
    confirmation = re.search(r"(确认|用户)\s*[:：].*\d{4}-\d{2}-\d{2}", spec_text + "\n" + tasks)
    return ("⚠️ 阻塞收口" in spec_text and "⚠️ 阻塞交付" in tasks and confirmation is not None)


def check_tasks(change: Path, mode: str, spec_text: str, check_ids: dict[str, str] | None,
                f: Findings, legacy: bool) -> None:
    path = change / "tasks.md"
    if not path.is_file():
        f.error("tasks.md 缺失")
        return
    tasks = read(path)
    check_handoff(tasks, f, legacy)
    check_closure(tasks, mode, legacy, f)
    states = task_states(tasks)
    if not states:
        f.error("tasks.md 没有任务复选框")

    closure_sec = section(tasks, "收口")
    closure_states = task_states(closure_sec) if closure_sec is not None else []
    closure_unchecked = sum(1 for s, _ in closure_states if s == " ")
    unchecked = [d for s, d in states if s == " "]
    build_unchecked = max(0, len(unchecked) - closure_unchecked)
    blocked = [d for s, d in states if s == "!"]
    if mode == "close":
        if build_unchecked:
            hint_unchecked = [d for d in unchecked if BLOCKED_HINT.search(d)]
            if hint_unchecked:
                f.error(f"tasks 仍有 {build_unchecked} 个未完成项（[ ]），其中 {len(hint_unchecked)} 项含阻塞标记；先改 [!] 并走阻塞收口")
            else:
                f.error(f"tasks 仍有 {build_unchecked} 个未完成项（[ ]）")
        if blocked:
            if not has_blocked_closure(spec_text, tasks):
                f.error("存在 [!] 阻塞项，但未走「阻塞收口」（spec 顶部需 ⚠️ 阻塞收口，tasks 需 ⚠️ 阻塞交付 + 用户确认日期）")

    if mode != "close":
        return

    sec = section(tasks, "验收结果")
    tab = find_table(sec, ("ID", "判定"))
    if tab is None:
        if legacy:
            f.warn("legacy（retroactive）：缺「验收结果」表，跳过验收判定检查")
            return
        f.error("tasks 缺少「验收结果」表（ID/判定）")
        return
    header, rows = tab
    id_i = column(header, "ID")
    verdict_i = column(header, "判定")
    target_i = column(header, "目标")
    actual_i = column(header, "实测")
    result_ids: set[str] = set()
    for row in rows:
        rid = cell(row, id_i)
        raw_verdict = cell(row, verdict_i)
        verdict, suffix = parse_verdict(raw_verdict)
        if not C_ID.match(rid):
            f.error(f"验收结果 ID 非法：{rid!r}")
            continue
        if rid in result_ids:
            f.error(f"验收结果 ID 重复：{rid}")
        result_ids.add(rid)
        if verdict is None:
            f.error(f"验收结果 {rid} 判定必须以 ✅/❌/⚠️ 开头（当前 {raw_verdict!r}）")
            continue
        if verdict == "❌" and suffix and not any(k in suffix for k in ("未通过", "证伪")):
            f.error(f"验收结果 {rid} 的 ❌ 后缀只能是「未通过（证伪）」（当前 {raw_verdict!r}）")
        if verdict == "⚠️" and suffix and "阻塞交付" not in suffix:
            f.error(f"验收结果 {rid} 的 ⚠️ 后缀只能是「阻塞交付」（当前 {raw_verdict!r}）")
        f.verdicts[{"✅": "pass", "❌": "fail", "⚠️": "blocked"}[verdict]] += 1
        if verdict == "✅":
            actual = cell(row, actual_i)
            if not actual or actual in ("—", "-", "待测", "TBD", "<实测>"):
                f.error(f"验收结果 {rid} 判定为 ✅，但「实测」为空或占位")
            else:
                ok = numeric_compare(cell(row, target_i), actual)
                if ok is False:
                    f.error(f"验收结果 {rid} 实测 {actual!r} 不满足目标 {cell(row, target_i)!r}")
        if verdict == "⚠️" and not has_blocked_closure(spec_text, tasks):
            f.error(f"验收结果 {rid} 标了 ⚠️ 阻塞交付，但未走「阻塞收口」（spec 标 ⚠️ 阻塞收口 + tasks 记 ⚠️ 阻塞交付 + 用户确认日期）")

    if check_ids:
        for cid in check_ids:
            if cid not in result_ids:
                f.error(f"check {cid} 在 tasks 验收结果中没有对应行")

    m = re.search(r"^\s*最终\s*[:：]\s*(.+)$", tasks, re.M)
    final = m.group(1).strip() if m else ""
    if not final:
        f.error("tasks 缺「最终：」行（通过 / ⚠️ 阻塞交付 / ❌ 未通过（证伪））")
    elif f.verdicts["fail"]:
        if "未通过" not in final and "证伪" not in final:
            f.error(f"存在 ❌ 未通过，但「最终：」写的是 {final!r}；应写「最终：❌ 未通过（证伪）」")
    elif blocked:
        if "阻塞" not in final or "通过" in final:
            f.error(f"存在 [!] 阻塞任务，「最终：」应写「⚠️ 阻塞交付」（不得写通过），当前 {final!r}")
    elif f.verdicts["blocked"]:
        if "阻塞" not in final or "通过" in final:
            f.error(f"存在 ⚠️ 阻塞交付，「最终：」应写「⚠️ 阻塞交付」（不得写通过），当前 {final!r}")
    elif "未通过" in final or "证伪" in final:
        f.error(f"验收结果没有 ❌，但「最终：」写的是 {final!r}；应改为「最终：通过」")
    elif any(k in final for k in ("未验证", "未完成", "阻塞", "待补")):
        f.error(f"验收结果全部通过，但「最终：」含未验证/阻塞字样：{final!r}")

    if f.verdicts["fail"]:
        design_text = read(change / "design.md") if (change / "design.md").is_file() else ""
        if not has_rejection(spec_text, design_text, tasks):
            f.error("存在 ❌ 未通过，但未走「证伪留档」：spec 顶部标 > ⚠️ 证伪，状态: 拒绝；design 加 §证伪记录；tasks 记 最终：❌ 未通过")
        else:
            f.rejected = True

    if not legacy:
        root = project_root(change)
        for state, desc in states:
            if state in "xX":
                if BLOCKED_HINT.search(desc) or UNVERIFIED.search(desc):
                    f.error(f"任务标 [x] 但含阻塞/未验证标记：{desc[:60]}")
                check_evidence(desc, change, root, f)


def check_project_spec(change: Path, mode: str, f: Findings, legacy: bool) -> None:
    if mode != "close":
        return
    parts = change.resolve().parts
    if "0_workbench" not in parts:
        f.warn("change 不在 0_workbench 下，跳过项目级 spec 变更记录检查")
        return
    idx = parts.index("0_workbench")
    root = Path(*parts[: idx + 1])
    design = root / "design"
    design_empty = design.is_dir() and not any(design.iterdir())
    if not design.is_dir() or design_empty:
        msg = "项目级 0_workbench/design/ 缺失或为空：归档前先补骨架并把 design 要点合并进去"
        if legacy:
            f.warn("legacy（retroactive）：" + msg)
        else:
            f.error(msg)
    pspec = root / "spec.md"
    if not pspec.is_file():
        f.error("项目级 0_workbench/spec.md 缺失")
        return
    text = read(pspec)
    sec = section(text, "变更记录")
    if sec is None:
        f.error("项目级 spec.md 缺少「变更记录」小节")
        return
    for line in sec.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("|") and set(stripped) <= set("|-: "):
            continue
        if "|" in stripped:
            cells = split_row(stripped)
            if change.name in cells:
                return
    f.error(f"项目级 spec.md 的「变更记录」没有 {change.name} 行；请加：| YYYY-MM-DD | {change.name} | 改了什么 |")


def main() -> int:
    ap = argparse.ArgumentParser(description="qwork 变更门（dispatch/close）")
    ap.add_argument("change", help="change 目录")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dispatch", action="store_true", help="派发前检查（默认）")
    mode.add_argument("--close", action="store_true", help="收口前检查")
    ap.add_argument("--strict", action="store_true", help="warning 也算失败")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()

    change = Path(args.change).resolve()
    mode_name = "close" if args.close else "dispatch"
    f = Findings()

    if not change.is_dir():
        f.error(f"目录不存在：{change}")
        return emit(f, mode_name, args)

    if not (change / "design.md").is_file():
        f.error("design.md 缺失")
    elif not read(change / "design.md").strip():
        f.error("design.md 为空")

    spec_text = read(change / "spec.md") if (change / "spec.md").is_file() else ""
    legacy = is_retroactive(spec_text)
    spec_ids = check_spec(change, f, legacy)
    check_ids = check_check(change, spec_ids, f, legacy)
    check_tasks(change, mode_name, spec_text, check_ids, f, legacy)
    check_project_spec(change, mode_name, f, legacy)
    return emit(f, mode_name, args)


def emit(f: Findings, mode: str, args: argparse.Namespace) -> int:
    ok = f.ok(args.strict)
    if args.json:
        print(json.dumps({
            "ok": ok,
            "mode": mode,
            "strict": args.strict,
            "errors": f.errors,
            "warnings": f.warnings,
            "verdicts": f.verdicts,
            "rejected": f.rejected,
            "summary": {"errors": len(f.errors), "warnings": len(f.warnings)},
        }, ensure_ascii=False, indent=2))
    else:
        for msg in f.errors:
            print(f"ERROR   {msg}")
        for msg in f.warnings:
            print(f"WARNING {msg}")
        if any(f.verdicts.values()):
            extra = "（证伪留档）" if f.rejected else ""
            print(f"判定: {f.verdicts['pass']} ✅ / {f.verdicts['fail']} ❌ / {f.verdicts['blocked']} ⚠️{extra}")
        print(f"{mode}: {len(f.errors)} error(s), {len(f.warnings)} warning(s) -> {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
