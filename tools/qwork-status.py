#!/usr/bin/env python3
"""qwork 进度总览：扫 0_workbench 的 change/ 与 archive/，给四要素、任务、C 覆盖与下一步。

用法:
  python3 tools/qwork-status.py [项目根或子目录] [--json]

只读，不修改任何文件。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

FOUR = ("spec.md", "design.md", "tasks.md", "check.md")
FENCE = re.compile(r"^\s*(```|~~~)")
CHECKBOX = re.compile(r"^\s*-\s+\[( |x|X|!)\]\s+(.*)$")
SPEC_ROW = re.compile(r"^\|\s*(S\d+)\s*\|", re.M)
CHECK_ROW = re.compile(r"^\|\s*(C\d+)\s*\|", re.M)
CHECK = Path(__file__).with_name("qwork-check.py")


def find_workbench(start: Path) -> Path | None:
    for p in [start, *start.parents]:
        if (p / "0_workbench").is_dir():
            return p / "0_workbench"
    return None


def section(text: str, *keywords: str) -> str:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and any(k in line for k in keywords):
            start = i + 1
            break
    if start is None:
        return ""
    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        out.append(line)
    return "\n".join(out)


def has_section(text: str, *keywords: str) -> bool:
    return any(line.startswith("## ") and any(k in line for k in keywords) for line in text.splitlines())


def task_stats(text: str) -> tuple[int, int, int]:
    total = done = blocked = 0
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = CHECKBOX.match(line)
        if not m:
            continue
        total += 1
        if m.group(1) in "xX":
            done += 1
        elif m.group(1) == "!":
            blocked += 1
    return total, done, blocked


def c_ids(text: str) -> set[str]:
    return set(CHECK_ROW.findall(text))


def close_gate(change: Path) -> tuple[int, list[str]] | None:
    """终态复用 close 门，避免 status 说可归档而 check FAIL。"""
    if not CHECK.is_file():
        return None
    p = subprocess.run([sys.executable, str(CHECK), str(change), "--close", "--json"],
                       text=True, capture_output=True)
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        detail = (p.stderr or p.stdout).strip()
        return p.returncode, [detail] if detail else []
    return p.returncode, list(data.get("errors") or [])


def inspect(change: Path, archived: bool, wb: Path) -> dict:
    files = {n: (change / n).is_file() for n in FOUR}
    missing = [n for n, ok in files.items() if not ok]
    spec = (change / "spec.md").read_text(encoding="utf-8") if files["spec.md"] else ""
    tasks = (change / "tasks.md").read_text(encoding="utf-8") if files["tasks.md"] else ""
    check = (change / "check.md").read_text(encoding="utf-8") if files["check.md"] else ""

    s_ids = sorted(set(SPEC_ROW.findall(spec)), key=lambda x: int(x[1:]))
    c_ids_check = sorted(c_ids(check), key=lambda x: int(x[1:]))
    results = section(tasks, "验收结果")
    c_ids_result = sorted(c_ids(results), key=lambda x: int(x[1:]))
    missing_results = [c for c in c_ids_check if c not in set(c_ids_result)]
    total, done, blocked = task_stats(tasks)
    unchecked = total - done - blocked
    pspec = wb / "spec.md"
    spec_logged = pspec.is_file() and change.name in pspec.read_text(encoding="utf-8")
    closure_present = has_section(tasks, "收口")
    ctotal, cdone, cblocked = task_stats(section(tasks, "收口")) if closure_present else (0, 0, 0)
    cunchecked = ctotal - cdone - cblocked
    build_unchecked = max(0, unchecked - cunchecked)

    if archived:
        state, action = "已归档", "—"
    elif missing:
        state, action = "缺四要素", "补 " + "、".join(missing)
    elif total == 0:
        state, action = "无任务", "写 tasks"
    elif blocked:
        state = f"阻塞（{blocked}）"
        action = "走阻塞收口" if "阻塞收口" in spec else "解除阻塞"
    elif build_unchecked:
        state, action = f"施工中（剩 {build_unchecked}）", "继续施工"
    elif not closure_present:
        state, action = "待收口（缺收口段）", "补 tasks 收口段"
    elif cunchecked:
        state, action = f"待收口（收口剩 {cunchecked}）", "完成收口项"
    elif missing_results:
        state, action = f"待收口（缺 {len(missing_results)} 个 C 结果）", "回填验收结果"
    elif not spec_logged:
        state, action = "待收口（项目 spec 未记）", "补 spec changelog"
    else:
        gate = close_gate(change)
        if gate is None:
            state, action = "待收口（缺 qwork-check.py）", "补 tools/qwork-check.py"
        elif gate[0] == 0:
            state, action = "可归档", "跑 qwork-archive"
        else:
            errors = gate[1]
            first = errors[0] if errors else "close 门未过"
            state, action = f"待收口（close 门 {len(errors) or 1} error）", first

    return {
        "name": change.name,
        "location": "archive" if archived else "change",
        "files": files,
        "missing": missing,
        "spec_ids": s_ids,
        "check_ids": c_ids_check,
        "result_ids": c_ids_result,
        "missing_results": missing_results,
        "tasks": {"total": total, "done": done, "blocked": blocked, "unchecked": unchecked},
        "closure": {"present": closure_present, "total": ctotal, "done": cdone, "blocked": cblocked, "unchecked": cunchecked},
        "project_spec_logged": spec_logged,
        "state": state,
        "next": action,
    }


def scan(wb: Path) -> list[dict]:
    out: list[dict] = []
    for location, archived in (("change", False), ("archive", True)):
        base = wb / location
        if not base.is_dir():
            continue
        for d in sorted(base.iterdir(), key=lambda p: p.name):
            if not d.is_dir() or d.name.startswith("."):
                continue
            out.append(inspect(d, archived, wb))
    return out


def human(wb: Path, rows: list[dict]) -> None:
    print(f"项目: {wb.parent}")
    if not rows:
        print("（change/ 与 archive/ 下都没有 change）")
        return
    print(f"{'位置':<8} {'change':<24} {'四要素':<6} {'tasks':<10} {'收口':<8} {'C 覆盖':<10} {'状态':<20} 下一步")
    for r in rows:
        four = "✓" if not r["missing"] else "缺" + str(len(r["missing"]))
        t = r["tasks"]
        c = r["closure"]
        tasks = f"{t['done']}/{t['total']}" if t["total"] else "—"
        closure = "缺" if not c["present"] else (f"{c['done']}/{c['total']}" if c["total"] else "空")
        cover = f"{len(set(r['result_ids']) & set(r['check_ids']))}/{len(r['check_ids'])}"
        print(f"{r['location']:<8} {r['name']:<24} {four:<6} {tasks:<10} {closure:<8} {cover:<10} {r['state']:<20} {r['next']}")
    active = sum(1 for r in rows if r["location"] == "change")
    print(f"\n合计：{active} 个在 change/，{len(rows) - active} 个在 archive/")


def main() -> int:
    ap = argparse.ArgumentParser(description="qwork 进度总览")
    ap.add_argument("path", nargs="?", default=".", help="项目根或任意子目录（默认当前目录）")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()

    start = Path(args.path).resolve()
    wb = find_workbench(start)
    if wb is None:
        print(f"❌ 找不到 0_workbench（从 {start} 向上）", file=sys.stderr)
        return 1
    rows = scan(wb)
    if args.json:
        print(json.dumps({
            "project": str(wb.parent),
            "changes": rows,
            "summary": {
                "change": sum(1 for r in rows if r["location"] == "change"),
                "archive": sum(1 for r in rows if r["location"] == "archive"),
            },
        }, ensure_ascii=False, indent=2))
    else:
        human(wb, rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
