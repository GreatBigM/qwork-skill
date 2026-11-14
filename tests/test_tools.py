"""qwork 工具回归（pytest）。全部在 tmp_path 内建仓，不动真实项目。"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "tools" / "qwork-check.py"
ARCHIVE = ROOT / "tools" / "qwork-archive.py"
STATUS = ROOT / "tools" / "qwork-status.py"
EXAMPLE = ROOT / "examples" / "doc-change"


def run(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], cwd=str(cwd),
                          text=True, capture_output=True)


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    assert p.returncode == 0, p.stderr
    return p


def make_project(tmp_path: Path, name: str = "demo") -> tuple[Path, Path]:
    root = tmp_path / "proj"
    change = root / "0_workbench" / "change" / name
    change.parent.mkdir(parents=True)
    shutil.copytree(EXAMPLE, change)
    # 用用户确认证据，避免依赖 fixture 里的 commit hash / 文件路径
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("→ 证据: data/evidence.md", "→ 用户确认: 用户 2026-11-14 验收")
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    (root / "0_workbench" / "spec.md").write_text(
        "# 项目\n\n## 变更记录\n\n| 日期 | change | 摘要 |\n|------|--------|------|\n"
        f"| 2026-11-14 | {name} | 测试 |\n", encoding="utf-8")
    # 另一个 change 的未提交改动，用于验证 archive 不越界
    other = root / "0_workbench" / "change" / "other"
    other.mkdir()
    (other / "tasks.md").write_text("# other\n", encoding="utf-8")
    git(root, "init", "-q")
    git(root, "config", "user.name", "Test")
    git(root, "config", "user.email", "test@example.com")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "init")
    return root, change


def test_close_passes_with_confirmations(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "0 error(s)" in p.stdout


def test_close_rejects_failed_verdict_without_rejection(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("| C1 | S1: 3/3 | 3/3 | ✅ |", "| C1 | S1: 3/3 | 3/3 | ❌ |")
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "证伪留档" in p.stdout + p.stderr


def test_close_rejects_fake_commit_evidence(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("→ 用户确认: 用户 2026-11-14 验收",
                          "→ commit deadbee", 1)
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "commit 证据不存在" in p.stdout + p.stderr


def test_project_spec_prose_is_not_a_changelog_row(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    spec = root / "0_workbench" / "spec.md"
    spec.write_text("# 项目\n\n## 变更记录\n\ndemo 在正文里提一句不算。\n", encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "变更记录" in p.stdout + p.stderr


def test_status_uses_close_gate(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    check = (change / "check.md").read_text(encoding="utf-8")
    check = check.replace("| C1 | S1 |", "| C1 | S9 |")
    (change / "check.md").write_text(check, encoding="utf-8")
    p = run(STATUS, str(root), cwd=root)
    assert p.returncode == 0, p.stderr
    assert "close 门" in p.stdout


def test_dispatch_strict_passes_new_change(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    (change / "tasks.md").write_text(tasks.replace("- [x]", "- [ ]"), encoding="utf-8")
    p = run(CHECK, str(change), "--dispatch", "--strict", cwd=root)
    assert p.returncode == 0, p.stdout + p.stderr


def test_archive_commit_only_archive_paths(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    other = root / "0_workbench" / "change" / "other" / "tasks.md"
    other.write_text("# other\n\nDIRTY\n", encoding="utf-8")
    p = run(ARCHIVE, str(change), "--commit", cwd=root)
    assert p.returncode == 0, p.stdout + p.stderr
    files = git(root, "show", "--name-only", "--format=", "HEAD").stdout.split()
    assert files and all(f.startswith("0_workbench/archive/demo/") for f in files), files
    assert "0_workbench/change/other/tasks.md" not in files
    status = git(root, "status", "--porcelain").stdout
    assert "0_workbench/change/other/tasks.md" in status


def test_archive_rolls_back_on_commit_failure(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    hook = root / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    hook.chmod(0o755)
    p = run(ARCHIVE, str(change), "--commit", cwd=root)
    assert p.returncode != 0
    assert change.is_dir()
    assert not (root / "0_workbench" / "archive" / "demo").exists()
    status = git(root, "status", "--porcelain").stdout
    assert "0_workbench/archive/" not in status


def test_close_accepts_rejection_with_archive_marker(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    spec = (change / "spec.md").read_text(encoding="utf-8")
    (change / "spec.md").write_text("> ⚠️ 证伪，状态: 拒绝\n" + spec, encoding="utf-8")
    design = (change / "design.md").read_text(encoding="utf-8")
    (change / "design.md").write_text(design + "\n## 证伪记录\n\n否决链。\n", encoding="utf-8")
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("| C1 | S1: 3/3 | 3/3 | ✅ |", "| C1 | S1: 3/3 | 3/3 | ❌ 未通过（证伪） |")
    tasks = tasks.replace("最终：通过", "最终：❌ 未通过")
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode == 0, p.stdout + p.stderr


def test_numeric_target_is_compared(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("| C3 | S3: ≤15 min | 14 min | ✅ |",
                          "| C3 | S3: ≤15 min | 25 min | ✅ |")
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "不满足目标" in p.stdout + p.stderr


def test_numeric_target_with_trailing_words_is_not_compared(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("| C3 | S3: ≤15 min | 14 min | ✅ |",
                          "| C3 | S3: >24h 拒绝 | 24h=86400；25h exit 2 | ✅ |")
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode == 0, p.stdout + p.stderr
