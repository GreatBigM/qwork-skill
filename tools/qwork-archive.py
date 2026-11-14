#!/usr/bin/env python3
"""qwork 归档事务：过 close 门 → git mv → 补 archive 侧 ignore → 复核 →（可选）提交。

用法:
  python3 tools/qwork-archive.py <change-dir|name> [--dry-run] [--commit] [--force]

- 默认先跑 `qwork-check.py --close`，不过不移动；`--force` 跳过门（不推荐）。
- 被 git 跟踪用 `git mv`，否则普通移动；移动后把 .gitignore 的 `change/` 规则镜像到 `archive/`。
- `--commit` 只提交本次归档相关路径；默认只打印提交命令。
- 失败会回滚移动与 .gitignore。
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

CHECK = Path(__file__).with_name("qwork-check.py")
FOUR = ("spec.md", "design.md", "tasks.md", "check.md")


class Fail(Exception):
    pass


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
    if check and p.returncode != 0:
        detail = (p.stderr or p.stdout).strip()
        raise Fail(detail or f"命令失败：{' '.join(cmd)}")
    return p


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return run(["git", "-C", str(root), *args], check=check)


def find_project(start: Path) -> Path | None:
    for p in [start, *start.parents]:
        if (p / "0_workbench").is_dir():
            return p
    return None


def resolve(arg: str) -> tuple[Path, Path]:
    raw = Path(arg)
    if raw.exists():
        change = raw.resolve()
    else:
        cwd = Path.cwd().resolve()
        root = find_project(cwd)
        if root is None:
            raise Fail("找不到 0_workbench；请传 change 路径")
        change = (root / "0_workbench" / "change" / arg).resolve()
    root = find_project(change)
    if root is None:
        raise Fail(f"change 不在 0_workbench 下：{change}")
    wb = root / "0_workbench"
    if change.parent == wb / "archive":
        raise Fail(f"该 change 已在 archive/：{change}")
    if change.parent != wb / "change":
        raise Fail(f"change 必须位于 {wb / 'change'}/ 下：{change}")
    missing = [n for n in FOUR if not (change / n).is_file()]
    if missing:
        raise Fail(f"不是完整 change 目录（缺 {', '.join(missing)}）：{change}")
    return root, change


def is_git(root: Path) -> bool:
    return git(root, "rev-parse", "--is-inside-work-tree", check=False).returncode == 0


def tracked(root: Path, rel: str) -> bool:
    return bool(git(root, "ls-files", "--", rel, check=False).stdout.strip())


def read_ignore(root: Path) -> tuple[Path, str]:
    path = root / ".gitignore"
    return path, (path.read_text(encoding="utf-8") if path.is_file() else "")


def write_ignore(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def ignore_additions(text: str) -> list[str]:
    lines = text.splitlines()
    adds: list[str] = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "0_workbench/change/" in s:
            candidate = s.replace("0_workbench/change/", "0_workbench/archive/", 1)
        elif s.startswith("change/") or "/change/" in s:
            candidate = s.replace("change/", "archive/", 1)
        else:
            continue
        if candidate not in lines and candidate not in adds:
            adds.append(candidate)
    return adds


def append_ignore(path: Path, text: str, additions: list[str]) -> str:
    if not additions:
        return text
    if text and not text.endswith("\n"):
        text += "\n"
    text += "\n".join(additions) + "\n"
    write_ignore(path, text)
    return text


def untracked_under(root: Path, rel: str) -> list[str]:
    p = git(root, "status", "--porcelain", "--untracked-files=all", "--", rel, check=False)
    return [line[3:].strip() for line in p.stdout.splitlines() if line.startswith("?? ")]


def fix_archive_ignore(root: Path, rel_new: str, name: str) -> list[str]:
    """把移动后新冒出的 data/ untracked 重新 ignore；返回仍未被 ignore 的路径。"""
    for _ in range(3):
        items = untracked_under(root, rel_new)
        if not items:
            return []
        data_items = [u for u in items if "/data/" in u or u.endswith("/data")]
        if not data_items:
            return items
        path, text = read_ignore(root)
        pattern = f"0_workbench/archive/{name}/data/"
        if pattern in text.splitlines():
            return items
        write_ignore(path, text + ("" if not text or text.endswith("\n") else "\n") + pattern + "\n")
    return untracked_under(root, rel_new)


def move(root: Path, change: Path, target: Path, is_tracked: bool) -> None:
    rel_old = change.relative_to(root).as_posix()
    rel_new = target.relative_to(root).as_posix()
    if is_tracked:
        git(root, "mv", rel_old, rel_new)
    else:
        shutil.move(str(change), str(target))


def move_back(root: Path, change: Path, target: Path, is_tracked: bool) -> None:
    rel_old = change.relative_to(root).as_posix()
    rel_new = target.relative_to(root).as_posix()
    if not target.exists():
        return
    if is_tracked:
        git(root, "mv", rel_new, rel_old, check=False)
    else:
        shutil.move(str(target), str(change))


def run_gate(change: Path) -> tuple[int, dict, str]:
    if not CHECK.is_file():
        raise Fail(f"缺少检查器：{CHECK}")
    p = subprocess.run([sys.executable, str(CHECK), str(change), "--close", "--json"],
                       text=True, capture_output=True)
    data: dict = {}
    if p.stdout.strip():
        try:
            data = json.loads(p.stdout)
        except json.JSONDecodeError:
            pass
    return p.returncode, data, p.stdout


def print_gate_failure(data: dict, raw_stdout: str) -> None:
    errors = data.get("errors") or []
    if errors:
        print("❌ close 门未过：", file=sys.stderr)
        for e in errors:
            print(f"   - {e}", file=sys.stderr)
    else:
        print("❌ close 门未过（无 JSON 详情）：", file=sys.stderr)
        if raw_stdout.strip():
            print(raw_stdout.strip(), file=sys.stderr)


def commit(root: Path, change: Path, target: Path, name: str) -> str:
    rel_old = change.relative_to(root).as_posix()
    rel_new = target.relative_to(root).as_posix()
    p = git(root, "add", "-A", "--", rel_old, rel_new, ".gitignore", check=False)
    if p.returncode != 0:
        git(root, "add", "-A", "--", "0_workbench", ".gitignore")
    if git(root, "diff", "--cached", "--quiet", check=False).returncode == 0:
        return ""
    git(root, "commit", "-m", f"{name}: 归档收口")
    return git(root, "rev-parse", "--short", "HEAD").stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="qwork 归档事务")
    ap.add_argument("change", help="change 目录或 name")
    ap.add_argument("--dry-run", action="store_true", help="只预演，不改文件")
    ap.add_argument("--commit", action="store_true", help="提交归档改动（默认只打印命令）")
    ap.add_argument("--force", action="store_true", help="跳过 close 门（不推荐）")
    args = ap.parse_args()

    try:
        root, change = resolve(args.change)
        name = change.name
        wb = root / "0_workbench"
        target = wb / "archive" / name
        if target.exists():
            raise Fail(f"归档目标已存在：{target}")

        code, data, raw = run_gate(change)
        gate_ok = code == 0
        if not gate_ok:
            print_gate_failure(data, raw)
            if not args.force:
                print("先修完再归档；确需跳过加 --force（不推荐）。", file=sys.stderr)
                return 1
            print("⚠️ --force：跳过 close 门，继续归档", file=sys.stderr)

        repo = is_git(root)
        is_tracked = repo and tracked(root, change.relative_to(root).as_posix())
        rel_old = change.relative_to(root).as_posix()
        rel_new = target.relative_to(root).as_posix()
        _, ignore_text = read_ignore(root)
        additions = ignore_additions(ignore_text)

        if args.dry_run:
            print(f"项目根   : {root}")
            print(f"change   : {rel_old}")
            print(f"归档到   : {rel_new}")
            print(f"git 跟踪 : {'是（git mv）' if is_tracked else '否（普通移动）'}")
            print(f"close 门 : {'PASS' if gate_ok else 'FAIL（--force 才会继续）'}")
            print(f"ignore + : {additions or '（无镜像规则；移动后按 data/ untracked 兜底）'}")
            print("预演结束：未改任何文件。")
            return 0 if gate_ok or args.force else 1

        if not repo:
            raise Fail("项目根不是 git 仓库；qwork 归档要求 git（否则无法复核移动与 ignore）")

        target.parent.mkdir(parents=True, exist_ok=True)
        backup = ignore_text
        moved = False
        try:
            move(root, change, target, is_tracked)
            moved = True
            path, text = read_ignore(root)
            append_ignore(path, text, additions)
            leftovers = fix_archive_ignore(root, rel_new, name)
            if leftovers:
                raise Fail("移动后仍有未 ignore 的未跟踪文件：\n  " + "\n  ".join(leftovers[:10]))
            # 复核：raw 应变为 ignored（!!），而不是 untracked（??）
            check = untracked_under(root, rel_new)
            if check:
                raise Fail("复核失败，archive 下仍有 untracked：\n  " + "\n  ".join(check[:10]))
        except Exception:
            if moved:
                move_back(root, change, target, is_tracked)
            write_ignore(root / ".gitignore", backup)
            raise

        print(f"✅ 已归档：{rel_old} → {rel_new}")
        if additions:
            print("   .gitignore 镜像：")
            for a in additions:
                print(f"   + {a}")
        if args.commit:
            h = commit(root, change, target, name)
            if h:
                print(f"✅ 已提交 {h}：{name}: 归档收口")
            else:
                print("ℹ️ 没有可提交的变更")
        else:
            print("   下一步：git add -A 0_workbench .gitignore && git commit -m "
                  f"\"{name}: 归档收口\"")
            print("   （或加 --commit 让本工具提交）")
        return 0
    except Fail as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
