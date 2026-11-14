# qwork 工具回归（pytest + 手跑）

> 改 `tools/`、模板或门禁语义后跑。全部用临时仓，不动真实项目。
>
> 自动化：`python3 -m pytest -q tests/test_tools.py`（29 项，覆盖 close 证据/❌/最终结论/骨架/阻塞自洽/占位符/阈值副本/变更记录完整性/实测对 spec、项目 spec 表行、status/close 阻塞提示、dispatch strict、archive 提交边界/回滚/预演）。
> 以下为手工补充场景；历史记录中的「工作区干净」不等于「没有越界提交」，以 4.6.1 记录为准。

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

负向：删 tasks 的 `| C4 |` 结果行 → `--close` 报 `check C4 ... 没有对应行`；留一个施工任务 `[ ]` → 报未完成；删 `## 收口` 段 → `--dispatch` 和 `--close` 都报缺少收口段；收口段留一个 `[ ]` → `--close` 报收口段未完成。

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
- 留一个施工任务 `[ ]` → `施工中（剩 1）`
- 删收口段 → `待收口（缺收口段）`
- 收口段留一个 `[ ]` → `待收口（收口剩 1）`
- 删项目级 spec 的 change 行 → `待收口（项目 spec 未记）`
- 空目录 → `缺四要素`

## 2026-11-14 / 4.5.0 记录

- check：examples 两份 dispatch 0/0；clean fixture close 0/0；删 C4 行、改 S9、留 `[ ]` 均按预期 FAIL。
- archive：dry-run 计划正确；实际移动后 `git status` 仅 rename + `.gitignore`，raw 变 `!!`；`--commit` 提交 `demo: 归档收口`，工作区干净；门禁失败时未移动、未建 archive。
- status：pilot（legacy）显示 `施工中（剩 1）`、C 覆盖 0/0；缺结果 fixture 显示 `待收口（缺 1 个 C 结果）`；空 change 显示 `缺四要素`。

## 2026-11-14 / 4.6.0 记录

- check：examples 两份 close/dispatch 0/0；删收口段 → `tasks 缺少「收口」段`；收口段留 `[ ]` → `tasks 收口段仍有 1 项未完成`。
- archive：带收口段的 fixture dry-run PASS、移动后仅 rename + `.gitignore`、raw 变 `!!`；无收口段 fixture 被 close 门拒绝；无 `.gitignore` 的 fixture `--commit` 成功（提交 `demo: 归档收口`，工作区干净）。
- status：收口 3/3 → `可归档`；缺段 → `待收口（缺收口段）`；收口剩 1 → `待收口（收口剩 1）`；spec 未记 → `待收口（项目 spec 未记）`；JSON 含 `closure` 与 `project_spec_logged`。


## 2026-11-14 / 4.6.1 记录

- pytest：`11 passed`。
- check：examples 两份 `--close` 仍 0 error（项目级 spec 检查因不在 0_workbench 下给 warning）；全 ❌ → `存在 ❌ 未通过，但未走「证伪留档」`；假 hash → `commit 证据不存在或不可解析`；目标 ≤15 min、实测 25 min → `不满足目标`；项目 spec 正文提 change 名 → `变更记录` 报错；`--dispatch --strict` 对新 change PASS。
- archive：`--commit` 后 `git show --name-only` 仅 `0_workbench/archive/demo/*`；另一 change 的 dirty 文件仍留在工作区。pre-commit exit 1 → 命令失败，change 回到原路径、archive 无残留、`.gitignore` 恢复；不再有目录级 fallback。
- status：C 引用 S9 的 change 显示 `待收口（close 门 N error）`，不再自报「可归档」。


## 2026-11-14 / 4.6.2 记录

- pytest：`13 passed`。
- status：`[ ]` 同行写 `BLOCKED_ENV: 等待设备` → 输出 `阻塞（待确认 1）` 与 `改 [!]`；`--json` 的 `blocked_hints` 为 1。通用词「阻塞」不触发，必须显式 `BLOCKED_*` / `阻塞原因：` / `等待外部` / `等待依赖` / `无法继续`。

## 2026-11-14 / 4.6.3 记录

- pytest：`17 passed`。
- close：全 ✅ 但 `最终：❌ 未通过` → FAIL；删掉 `最终：` 行 → FAIL；`# 验收` 标题仍能识别表格。
- archive `--dry-run`：close 门 FAIL 时先打印项目根/归档路径/`close 门 : FAIL`/预演结束，再打印门禁 error。

## 2026-11-14 / 4.6.4 记录

- pytest：`29 passed`。
- close：空证据文件、`[x] BLOCKED_ENV`/`等待摄像头`、空 design、缺/空项目 `design/`、`最终：通过（P1 未验证）`、`[!]` 阻塞任务却写最终通过、`<命令>` 均 FAIL；practice 归档 change 仍 PASS。
