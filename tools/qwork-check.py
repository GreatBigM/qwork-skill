#!/usr/bin/env python3
"""qwork 变更门：检查 change 目录是否可派发（dispatch）或可收口（close）。

用法:
  python3 tools/qwork-check.py <change-dir> --dispatch [--strict] [--json]
  python3 tools/qwork-check.py <change-dir> --close    [--strict] [--json]

退出码: 0 = 通过；1 = 有 error（--strict 下 warning 也算失败）。
无外部依赖；只读，不改任何文件。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

S_ID = re.compile(r"^S\d+$")
C_ID = re.compile(r"^C\d+$")
STATUS_LINE = re.compile(r"^\s*-\s+\[( |x|X|!)\]\s+(.*)$")
FENCE = re.compile(r"^\s*(```|~~~)")

HANDOFF_FIELDS = ("必读", "环境", "禁止", "决策权", "启动条件", "停止", "判据", "回报")
VERDICTS = {"✅", "❌", "⚠️"}


class Findings:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

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
    for i, line in enumerate(lines):
        if line.startswith("## ") and any(k in line for k in keywords):
            start = i + 1
            break
    if start is None:
        return None
    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        out.append(line)
    return "\n".join(out)


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
        cells = [c.strip() for c in stripped.strip("|").split("|")]
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


def check_spec(change: Path, f: Findings) -> dict[str, str] | None:
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
        legacy = find_table(sec, ("维度", "基线", "目标"))
        if legacy is not None:
            f.warn("legacy spec：成功标准表无 ID 列，跳过 S/C 追踪检查（新 change 请用模板）")
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


def check_check(change: Path, spec_ids: dict[str, str] | None, f: Findings) -> dict[str, str] | None:
    path = change / "check.md"
    if not path.is_file():
        f.error("check.md 缺失")
        return None
    text = read(path)
    sec = section(text, "验收项", "验收方法", "验收")
    tab = find_table(sec, ("ID", "spec", "判定"))
    if tab is None:
        f.warn("legacy check：无 ID/spec/判定 表，跳过 C 追踪检查")
        return None
    header, rows = tab
    id_i = column(header, "ID")
    spec_i = column(header, "spec")
    method_i = column(header, "检查方法", "方法", "命令")
    verdict_i = column(header, "判定")
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
        if not cell(row, method_i):
            f.error(f"check {cid} 缺检查方法")
        if verdict_i is not None and not cell(row, verdict_i):
            f.error(f"check {cid} 缺判定口径")
        ids[cid] = ref
    if not ids:
        f.error("check 验收表没有有效数据行")
    if spec_ids:
        used = set(ids.values())
        for sid in spec_ids:
            if sid not in used:
                f.error(f"spec {sid} 没有任何 check 项覆盖")
    return ids or None


def check_handoff(tasks: str, f: Findings) -> None:
    sec = section(tasks, "接手须知")
    if sec is None:
        f.warn("legacy tasks：无「接手须知」，who/when 字段缺失")
        return
    for kw in HANDOFF_FIELDS:
        if kw not in sec:
            f.error(f"接手须知缺少「{kw}」")


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


def check_tasks(change: Path, mode: str, spec_text: str, check_ids: dict[str, str] | None, f: Findings) -> None:
    path = change / "tasks.md"
    if not path.is_file():
        f.error("tasks.md 缺失")
        return
    tasks = read(path)
    check_handoff(tasks, f)
    states = task_states(tasks)
    if not states:
        f.error("tasks.md 没有任务复选框")
    unchecked = [d for s, d in states if s == " "]
    blocked = [d for s, d in states if s == "!"]
    if mode == "close":
        if unchecked:
            f.error(f"tasks 仍有 {len(unchecked)} 个未完成项（[ ]）")
        if blocked:
            if "阻塞收口" not in spec_text or "⚠️ 阻塞交付" not in tasks:
                f.error("存在 [!] 阻塞项，但未走「阻塞收口」（spec 顶部需标 ⚠️ 阻塞收口，tasks 需记 ⚠️ 阻塞交付）")
    elif unchecked and not blocked:
        f.warn(f"派发前有 {len(unchecked)} 个未开始任务（正常，收口时必须清零）")

    if mode != "close":
        return
    sec = section(tasks, "验收结果")
    tab = find_table(sec, ("ID", "判定"))
    if tab is None:
        f.error("tasks 缺少「验收结果」表（ID/判定）")
        return
    header, rows = tab
    id_i = column(header, "ID")
    verdict_i = column(header, "判定")
    result_ids: set[str] = set()
    for row in rows:
        rid = cell(row, id_i)
        verdict = cell(row, verdict_i)
        if not C_ID.match(rid):
            f.error(f"验收结果 ID 非法：{rid!r}")
            continue
        if rid in result_ids:
            f.error(f"验收结果 ID 重复：{rid}")
        result_ids.add(rid)
        if verdict not in VERDICTS:
            f.error(f"验收结果 {rid} 判定必须是 ✅/❌/⚠️（当前 {verdict!r}）")
        if verdict == "⚠️" and "阻塞收口" not in spec_text:
            f.error(f"验收结果 {rid} 标了 ⚠️ 阻塞交付，但 spec 未标「⚠️ 阻塞收口」")
    if check_ids:
        for cid in check_ids:
            if cid not in result_ids:
                f.error(f"check {cid} 在 tasks 验收结果中没有对应行")


def check_project_spec(change: Path, mode: str, f: Findings) -> None:
    if mode != "close":
        return
    parts = change.resolve().parts
    if "0_workbench" not in parts:
        f.warn("change 不在 0_workbench 下，跳过项目级 spec 变更记录检查")
        return
    idx = parts.index("0_workbench")
    root = Path(*parts[: idx + 1])
    pspec = root / "spec.md"
    if not pspec.is_file():
        f.error("项目级 0_workbench/spec.md 缺失")
        return
    if change.name not in read(pspec):
        f.error(f"项目级 spec.md 的变更记录没有 {change.name} 行")


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
    for name in ("spec.md", "design.md", "check.md", "tasks.md"):
        if not (change / name).is_file():
            f.error(f"{name} 缺失")

    spec_text = read(change / "spec.md") if (change / "spec.md").is_file() else ""
    spec_ids = check_spec(change, f)
    check_ids = check_check(change, spec_ids, f)
    check_tasks(change, mode_name, spec_text, check_ids, f)
    check_project_spec(change, mode_name, f)
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
            "summary": {"errors": len(f.errors), "warnings": len(f.warnings)},
        }, ensure_ascii=False, indent=2))
    else:
        for msg in f.errors:
            print(f"ERROR   {msg}")
        for msg in f.warnings:
            print(f"WARNING {msg}")
        print(f"{mode}: {len(f.errors)} error(s), {len(f.warnings)} warning(s) -> {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
