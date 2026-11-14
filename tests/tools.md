# qwork 工具回归（手跑）

> 改 `tools/` 或模板后跑。用临时 git 仓，不动真实项目。

## 建 fixture

```bash
REPO=/path/to/qwork-skill
rm -rf /tmp/qwa-test && mkdir -p /tmp/qwa-test/0_workbench/change/demo/data/raw
cd /tmp/qwa-test && git init -q
git config user.name Test && git config user.email test@example.com
cp "$REPO"/examples/doc-change/*.md 0_workbench/change/demo/
printf '# 项目\n\n## 变更记录\n2026-11-14 | demo | 示例\n' > 0_workbench/spec.md
printf '0_workbench/change/*/data/**/raw/\n' > .gitignore
echo raw > 0_workbench/change/demo/data/raw/a.log
echo report > 0_workbench/change/demo/data/report.md
git add . && git commit -qm init
```

## 1. check

```bash
python3 "$REPO"/tools/qwork-check.py 0_workbench/change/demo --dispatch   # PASS
python3 "$REPO"/tools/qwork-check.py 0_workbench/change/demo --close      # PASS
```

负向：删 tasks 的 `| C4 |` 结果行 → `--close` 报 `check C4 ... 没有对应行`；留一个 `[ ]` → 报未完成。

## 2. archive

```bash
python3 "$REPO"/tools/qwork-archive.py 0_workbench/change/demo --dry-run   # 只打印 Plan
python3 "$REPO"/tools/qwork-archive.py 0_workbench/change/demo             # 移动 + 补 ignore
git status --porcelain                                                     # 只有 rename + .gitignore
git status --porcelain --ignored=matching | grep raw                       # !! archive/.../raw/
```

负向：把 tasks 改出一个 `[ ]` → 归档应 exit 1，change 仍在原处、无 archive 目录。
提交模式：新 fixture 上加 `--commit`，`git log -1 --format=%s` 应为 `demo: 归档收口`，`git status` 干净。

## 3. status

```bash
python3 "$REPO"/tools/qwork-status.py /tmp/qwa-test          # change/demo 可归档
python3 "$REPO"/tools/qwork-status.py /tmp/qwa-test --json   # 字段完整
```

- 删一条 C 结果 → `待收口（缺 1 个 C 结果）`
- 留一个 `[ ]` → `施工中（剩 1）`
- 空目录 → `缺四要素`

## 2026-11-14 / 4.5.0 记录

- check：examples 两份 dispatch 0/0；clean fixture close 0/0；删 C4 行、改 S9、留 `[ ]` 均按预期 FAIL。
- archive：dry-run 计划正确；实际移动后 `git status` 仅 rename + `.gitignore`，raw 变 `!!`；`--commit` 提交 `demo: 归档收口`，工作区干净；门禁失败时未移动、未建 archive。
- status：pilot（legacy）显示 `施工中（剩 1）`、C 覆盖 0/0；缺结果 fixture 显示 `待收口（缺 1 个 C 结果）`；空 change 显示 `缺四要素`。
