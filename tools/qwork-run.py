#!/usr/bin/env python3
"""执行 check.md 中「自动」验收项的命令，并把输出落到 change/data/check-<C>.log。

用法:
  python3 tools/qwork-run.py <change目录> [--dry-run] [--timeout 600]

只执行 check 表里明确标为「自动」且方法写在反引号中的命令；人工项/说明性步骤跳过。
这是可选的执行辅助，不替代 qwork-check：close 仍只校验记录与证据。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

FENCE = re.compile(r"^\s*(```|~~~)")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def section(text: str, *names: str) -> str | None:
    lines = text.splitlines()
    start = None
    want = tuple(n.lower() for n in names)
    for i, line in enumerate(lines):
        m = re.match(r"^#{1,3}\s+(.+?)\s*$", line)
        if not m:
            continue
        title = m.group(1).strip().lower()
        if any(title == w or title.startswith(w) for w in want):
            start = i + 1
            break
    if start is None:
        return None
    out: list[str] = []
    in_fence = False
    for line in lines[start:]:
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence and re.match(r"^#{1,3}\s+", line):
            break
        out.append(line)
    return "\n".join(out)


def split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def find_table(sec: str, required: tuple[str, ...]) -> tuple[list[str], list[list[str]]] | None:
    lines = sec.splitlines()
    for i, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        header = split_row(line)
        low = [h.lower() for h in header]
        if all(any(r.lower() in h for h in low) for r in required):
            rows = []
            for row in lines[i + 1:]:
                if not row.strip().startswith("|"):
                    break
                cells = split_row(row)
                if all(set(c) <= set("-: ") for c in cells):
                    continue
                rows.append(cells)
            return header, rows
    return None


def column(header: list[str], *names: str) -> int | None:
    for i, h in enumerate(header):
        if any(n.lower() in h.lower() for n in names):
            return i
    return None


def cell(row: list[str], idx: int | None) -> str:
    return row[idx] if idx is not None and idx < len(row) else ""


def project_root(change: Path) -> Path:
    parts = change.resolve().parts
    if "0_workbench" in parts:
        return Path(*parts[: parts.index("0_workbench")])
    return change.parent


def main() -> int:
    ap = argparse.ArgumentParser(description="执行 check.md 的自动项并落 data/ 日志")
    ap.add_argument("change", help="change 目录")
    ap.add_argument("--dry-run", action="store_true", help="只打印将执行的命令")
    ap.add_argument("--timeout", type=int, default=600, help="单条命令超时秒数（默认 600）")
    ap.add_argument("--only", default="", help="只跑指定 C ID，逗号分隔（如 C1,C3）")
    args = ap.parse_args()

    change = Path(args.change)
    check = change / "check.md"
    if not check.is_file():
        print(f"❌ check.md 缺失：{check}", file=sys.stderr)
        return 1
    tab = find_table(section(read(check), "验收项", "验收方法", "验收") or "", ("ID", "方法", "类型"))
    if tab is None:
        print("❌ check.md 没有 ID/方法/类型 的验收表", file=sys.stderr)
        return 1
    header, rows = tab
    id_i = column(header, "ID")
    method_i = column(header, "检查方法", "方法", "命令")
    type_i = column(header, "类型")
    root = project_root(change)
    data = change / "data"
    only = {x.strip().upper() for x in args.only.split(",") if x.strip()}
    ran = 0
    failed = 0
    for row in rows:
        cid = cell(row, id_i)
        typ = cell(row, type_i)
        method = cell(row, method_i)
        if not cid or typ != "自动":
            continue
        if only and cid.upper() not in only:
            continue
        m = re.search(r"`([^`]+)`", method)
        if not m:
            print(f"⏭  {cid} 自动项未写反引号命令，跳过：{method[:60]}")
            continue
        cmd = m.group(1).strip()
        if not cmd:
            continue
        ran += 1
        if args.dry_run:
            print(f"▶  {cid}: {cmd}")
            continue
        data.mkdir(parents=True, exist_ok=True)
        log = data / f"check-{cid}.log"
        try:
            p = subprocess.run(["bash", "-lc", cmd], cwd=root, text=True,
                               capture_output=True, timeout=args.timeout)
            out, err, rc = p.stdout, p.stderr, p.returncode
        except subprocess.TimeoutExpired as e:
            out = e.stdout or ""
            err = (e.stderr or "") + f"\nTIMEOUT after {args.timeout}s"
            rc = 124
        log.write_text(f"$ {cmd}\nexit={rc}\n\n--- stdout ---\n{out}\n--- stderr ---\n{err}\n",
                       encoding="utf-8")
        if rc == 0:
            print(f"✅ {cid} -> {log.relative_to(root)}")
        else:
            failed += 1
            print(f"❌ {cid} exit={rc} -> {log.relative_to(root)}")
    if args.dry_run:
        print(f"dry-run：{ran} 条自动命令；未执行、未写日志")
    else:
        print(f"执行完成：{ran} 条，失败 {failed} 条；日志在 {data.relative_to(root)}/")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
