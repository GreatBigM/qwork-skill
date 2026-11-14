"""qwork 工具回归（pytest）。全部在 tmp_path 内建仓，不动真实项目。"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "tools" / "qwork-check.py"
ARCHIVE = ROOT / "tools" / "qwork-archive.py"
STATUS = ROOT / "tools" / "qwork-status.py"
RUN = ROOT / "tools" / "qwork-run.py"
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
    design = root / "0_workbench" / "design"
    design.mkdir()
    (design / "notes.md").write_text("# design\n\n测试用。\n", encoding="utf-8")
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


def test_close_hints_unchecked_blocked_task(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("- [x]", "- [ ] BLOCKED_ENV: 等待设备", 1)
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "含阻塞标记" in p.stdout + p.stderr
    assert "改 [!]" in p.stdout + p.stderr


def test_close_rejects_missing_final_line(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = "\n".join(line for line in tasks.splitlines() if not line.startswith("最终："))
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "缺「最终" in p.stdout + p.stderr


def test_close_rejects_final_contradiction(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("最终：通过", "最终：❌ 未通过", 1)
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "没有 ❌" in p.stdout + p.stderr


def test_dry_run_prints_plan_when_gate_fails(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("| C1 | S1: 3/3 | 3/3 | ✅ |", "| C1 | S1: 3/3 | 3/3 | ❌ |")
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(ARCHIVE, str(change), "--dry-run", cwd=root)
    assert p.returncode != 0
    assert "项目根" in p.stdout
    assert "close 门 : FAIL" in p.stdout
    assert "预演结束" in p.stdout


def test_section_accepts_hash_heading(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    check = (change / "check.md").read_text(encoding="utf-8")
    check = check.replace("## 验收", "# 验收", 1)
    (change / "check.md").write_text(check, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode == 0, p.stdout + p.stderr


def test_close_rejects_missing_project_design(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    shutil.rmtree(root / "0_workbench" / "design")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "0_workbench/design/ 缺失" in p.stdout + p.stderr


def test_close_rejects_empty_evidence_file(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    evidence = change / "data" / "evidence.md"
    evidence.write_text("", encoding="utf-8")
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("→ 用户确认: 用户 2026-11-14 验收", "→ 证据: data/evidence.md")
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "证据文件为空" in p.stdout + p.stderr


def test_close_rejects_checked_blocked_task(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("- [x]", "- [x] BLOCKED_ENV: 等待设备", 1)
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "含阻塞/未验证标记" in p.stdout + p.stderr


def test_close_rejects_empty_design(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    (change / "design.md").write_text("", encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "design.md 为空" in p.stdout + p.stderr


def test_close_rejects_mixed_final(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("最终：通过", "最终：通过（P1 未验证）", 1)
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "含未验证/阻塞字样" in p.stdout + p.stderr


def test_close_rejects_placeholder_check_method(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    check = (change / "check.md").read_text(encoding="utf-8")
    check = check.replace("`bash scripts/build.sh --strict`", "`<命令>`", 1)
    (change / "check.md").write_text(check, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "检查方法仍是占位符" in p.stdout + p.stderr


def test_close_rejects_empty_project_design(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    design = root / "0_workbench" / "design"
    shutil.rmtree(design)
    design.mkdir()
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "design/ 缺失或为空" in p.stdout + p.stderr


def test_close_rejects_checked_waiting_task(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("- [x]", "- [x] 等待摄像头", 1)
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "含阻塞/未验证标记" in p.stdout + p.stderr


def test_close_rejects_blocked_task_with_final_pass(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    spec = (change / "spec.md").read_text(encoding="utf-8")
    (change / "spec.md").write_text("> ⚠️ 阻塞收口：等待设备\n" + spec, encoding="utf-8")
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("- [x]", "- [!] 等待设备（解除条件：设备到位后复测）", 1)
    tasks += "\n⚠️ 阻塞交付\n用户确认: 用户 2026-11-14\n"
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "存在 [!] 阻塞任务" in p.stdout + p.stderr


def test_close_rejects_numeric_threshold_in_check(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    check = change / "check.md"
    text = check.read_text(encoding="utf-8")
    text = text.replace("按 spec S3 目标判定（目标值见 spec）", "≤15 min", 1)
    check.write_text(text, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "判定口径含数值比较/倍数" in p.stdout + p.stderr


def test_close_rejects_incomplete_project_spec_row(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    spec = root / "0_workbench" / "spec.md"
    spec.write_text("# 项目\n\n## 变更记录\n\n| 日期 | change | 摘要 |\n|------|--------|------|\n"
                    "| 2026-11-14 | demo | |\n", encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "行内容不完整" in p.stdout + p.stderr


def test_close_compares_actual_against_spec_target(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = change / "tasks.md"
    text = tasks.read_text(encoding="utf-8")
    text = text.replace("| C3 | S3: ≤15 min | 14 min | ✅ |", "| C3 | 按 spec S3 判定 | 25 min | ✅ |", 1)
    tasks.write_text(text, encoding="utf-8")
    p = run(CHECK, str(change), "--close", cwd=root)
    assert p.returncode != 0
    assert "不满足 spec S3 目标" in p.stdout + p.stderr


def test_status_wip_limit_and_strict(tmp_path: Path) -> None:
    root, _change = make_project(tmp_path)
    (root / "0_workbench" / "qwork.conf").write_text("wip_limit=1\n", encoding="utf-8")
    p = run(STATUS, str(root), "--json", cwd=root)
    assert p.returncode == 0, p.stdout + p.stderr
    data = json.loads(p.stdout)
    assert data["wip"] == {"limit": 1, "active": 2, "over": True}
    p = run(STATUS, str(root), "--strict", cwd=root)
    assert p.returncode == 1
    assert "超限" in p.stdout + p.stderr


def test_close_require_logs_rejects_missing(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    p = run(CHECK, str(change), "--close", "--require-logs", cwd=root)
    assert p.returncode != 0
    assert "自动项 C1 缺少 data/check-C1.log" in p.stdout + p.stderr


def test_close_require_logs_accepts_passing_logs(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    data = change / "data"
    data.mkdir(exist_ok=True)
    for cid in ("C1", "C2", "C3", "C4"):
        (data / f"check-{cid}.log").write_text("$ true\nexit=0\n", encoding="utf-8")
    p = run(CHECK, str(change), "--close", "--require-logs", cwd=root)
    assert p.returncode == 0, p.stdout + p.stderr


def test_run_executes_auto_check(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    check = change / "check.md"
    text = check.read_text(encoding="utf-8").replace("`bash scripts/build.sh --strict`", "`printf ok`", 1)
    check.write_text(text, encoding="utf-8")
    p = run(RUN, str(change), "--only", "C1", cwd=root)
    assert p.returncode == 0, p.stdout + p.stderr
    log = change / "data" / "check-C1.log"
    assert log.is_file() and "exit=0" in log.read_text(encoding="utf-8")


def test_run_reports_failed_auto_check(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    check = change / "check.md"
    text = check.read_text(encoding="utf-8").replace("`bash scripts/build.sh --strict`", "`false`", 1)
    check.write_text(text, encoding="utf-8")
    p = run(RUN, str(change), "--only", "C1", cwd=root)
    assert p.returncode == 1
    assert "exit=1" in (change / "data" / "check-C1.log").read_text(encoding="utf-8")


def test_status_reads_owner(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = change / "tasks.md"
    text = tasks.read_text(encoding="utf-8").replace("负责人：lead", "负责人：alice", 1)
    tasks.write_text(text, encoding="utf-8")
    p = run(STATUS, str(root), "--json", cwd=root)
    assert p.returncode == 0, p.stdout + p.stderr
    data = json.loads(p.stdout)
    assert data["changes"][0]["owner"] == "alice"


def test_status_flags_unchecked_blocked_hint(tmp_path: Path) -> None:
    root, change = make_project(tmp_path)
    tasks = (change / "tasks.md").read_text(encoding="utf-8")
    tasks = tasks.replace("- [x]", "- [ ] BLOCKED_ENV: 等待设备", 1)
    (change / "tasks.md").write_text(tasks, encoding="utf-8")
    p = run(STATUS, str(root), cwd=root)
    assert p.returncode == 0, p.stderr
    assert "阻塞（待确认 1）" in p.stdout
    assert "改 [!]" in p.stdout
    pj = run(STATUS, str(root), "--json", cwd=root)
    data = json.loads(pj.stdout)
    assert data["changes"][0]["blocked_hints"] == 1


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
