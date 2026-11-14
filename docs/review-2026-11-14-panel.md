# qwork 多角色评审报告（2026-11-14）

> 对象：qwork v4.6.0（源仓 `<repo>`，HEAD `5f99296`）。
> 方法：6 角色独立评审 → 定向互审 → lead 在 4.6.0 上逐条复验。
> 版本说明：评审期间仓库由 4.5.0 升到 4.6.0（tasks 唯一台账 + 收口段）；本文以 4.6.0 行为为准。部分 R1 行号取自 4.5.0/4.6.0 工作树，关键结论均已按 4.6.0 复跑。

> **修复状态（2026-11-14，v4.6.2）**：P0-1/P0-2 与 P1-1~P1-5 已修，pytest 26 项并通过 `/tmp/qwork-practice-461` 正/负向实践复验；P1-6 的“只读/只写”已改字段级权限，v4.6.2 补了 status/check 对 `[ ]` 同行阻塞标记的提示（自动改状态、owner/WIP 仍留 4.7）；v4.6.3 又补了 tasks「最终：」与判定一致性、`#` 验收标题、archive 失败预演计划；v4.6.4 补了证据非空/用户确认日期、`[x]` 阻塞自洽、项目 design 骨架（含空目录）、`[!]` 最终态、check 占位符；4.6.2 冷启动探针为「新建/改需求 勉强、收口 不能」；4.6.4 定向复验收口已转为「勉强（可正确收口）」，复验指出的空 design 目录与 `[!]` 写通过已补，剩余 C 命令执行/环境缺失三分留 4.7；P1-7 尚未推送远端；P1-8 采用成本仍待产品负责人拍板。以下正文保留评审时 v4.6.0 的记录。

---

## 0. 一页结论

**这 6 个角色不是并列的六个视角，而是一条链：规则定义 → 执行 → 实现 → 交付 → 对抗 → 价值。** 缺任何一段，评审都会漏掉一类问题：只做方法论会漏掉 archive 越界，只做工具会漏掉“规则本身自相矛盾”，只做红队会漏掉“团队根本不会用”。

| 角色 | 回答的问题 | 一句话结论 |
|---|---|---|
| 流程架构师 / 方法论审计 | 规则是否自洽、状态机是否闭合 | 四要素和 S/C 骨架成立，但门禁会给出假 PASS，状态机缺“废弃/重开” |
| 冷启动执行者 / 一线工程师 | 新会话只拿 change 目录，第一屏能不能照做 | 能照做一半：权限自相矛盾，阻塞被当成“继续施工” |
| 工具与自动化工程师 | check/archive/status 的实现是否可靠 | check 主路径可用；archive 越界提交且失败不回滚，status 与 close 不同源 |
| 技能工程与分发维护者 | 评审成果能不能到达用户 | 7 笔提交未推送，一键安装拿到的仍是 3.4.4；手动安装还漏 tools/examples |
| 红队 / 反模式审计 | 能不能不干活就过门 | 假证据、全 ❌、自称 legacy 三条路都实测走通 |
| 项目负责人 / ROI | 值不值得用、谁承担成本 | 适合有判据、要跨人交接的 change；小修和事故缺通道，3-5 人缺 owner/WIP |

**最危险的不是“规则不够多”，而是终局信号不可信：`close: PASS` 和“可归档”目前不能证明验收通过、证据存在、归档边界干净。** 其次是交付链：本机是 4.6.0，远端仍是 3.4.4，用户按 README 安装会拿到旧版并覆盖本机新版。

**建议先修 2 个 P0 + 4 个 P1，再发 4.6.1；不要原样推送 4.6.0。** 详见 §7。

---

## 1. 角色设置：为什么是这 6 个

| # | 角色 | 覆盖的失效模式 | 本轮实际抓到的问题 |
|---|---|---|---|
| 1 | 流程架构师 / 方法论审计 | 规则自相矛盾、状态机不闭合、宪法与模板冲突 | spec 阈值被 check 复制；SCHEMA 的验收表示例过不了自己的门；缺废弃/重开 |
| 2 | 冷启动执行者 / 一线工程师 | 规则“写给人看”但第一屏无法执行 | tasks 既“只读”又“只写”；pilot 的阻塞任务被显示成“继续施工”；熔断 3 次 vs 8 次预算 |
| 3 | 工具与自动化工程师 | 门禁/归档/状态实现与文档承诺不一致 | archive 越界提交、commit 失败不回滚；status 说可归档、close 说 FAIL；legacy 被硬拦 |
| 4 | 技能工程与分发维护者 | 版本、安装面、路由、机检、探针 | 7 笔未推送；手动安装漏 tools/examples；description 148 字；pre-push 名单漏项 |
| 5 | 红队 / 反模式审计 | 自证、伪造、结构逃逸、失败归档 | 假 hash/假路径 PASS；全 ❌ 仍 PASS 并 archive；改表头即降级；项目 spec 子串匹配 |
| 6 | 项目负责人 / ROI | 采用成本、协作粒度、责任归属 | 小修恒付满额成本；无 hotfix；无 owner/WIP/依赖；收口冲突落负责人 |

### 1.1 两轮怎么跑

- **R1 独立评审**：6 个角色各自读源码/文档/真实 pilot，给出 verdict、strengths、最多 6 条 finding；每条必须有 `file:line` + 原文/实测，禁止泛泛而谈。
- **R2 定向互审**：method↔redteam、executor↔maintainer、toolsmith↔pm 三组双向，逐条 `confirm / dispute / uncertain`，并补对方漏掉的问题。
- **lead 复验**：对 P0/P1 逐条在当前 4.6.0 上重跑；不采信“角色说成立”。
- **本轮限制**：R2 只完整捕获 3 份互审（method→redteam、redteam→method、executor→maintainer）；maintainer→executor、toolsmith↔pm 因 81KB 输出截断未纳入。R1 六角色与 lead 复验覆盖了主要结论；未捕获部分不影响 P0 判断。

### 1.2 评审边界

- 本轮**没有**做真实用户可用性测试；ROI 的“1.8 万字符/140 行”是实测工件规模，不是工时测量。
- 校验器是否该判“语义质量”存在角色分歧；本报告按**机械可判定**分层：路径存在、hash 可解析、数值比较、表格位置属于工具职责；论证是否充分仍属评审职责。
- 4.6.0 是评审期间出现的版本，4.5→4.6 的改动（收口段/status 项目 spec/archive 无 .gitignore）已计入，但不追溯 4.5 的旧结论。

---

## 2. 总评

| 维度 | 分数 | 判断 |
|---|---|---|
| 方法论 / 内容 | 8.5 | 四要素单一权威、S/C 追踪、证伪可归档、领域手册扎实 |
| 工件结构 | 8.0 | 模板/样例齐全；但 SCHEMA 示例与 checker 冲突 |
| 门禁可信度 | 4.5 | 全 ❌ 可 PASS，假证据可 PASS，项目 spec 可子串绕过 |
| 执行交接 | 6.0 | 权限矛盾、阻塞误报、预算冲突、接手须知只查关键词 |
| 工具可靠性 | 5.0 | archive 越界/不回滚，status 与 close 不同源 |
| 分发维护 | 5.0 | 7 笔未推送，手动安装缺目录，description 越限 |
| 采用成本 | 5.5 | 冷启动约 1.8 万字符，小修/事故无通道 |
| **综合** | **6.5** | 方法论强，工程可信度拖累；修完 P0/P1 可回到 8+ |

### 2.1 做对了什么

- **四要素的分工是清楚的**：spec 做成什么样、design 怎么做、tasks 怎么组织、check 怎么验收；S/C 稳定 ID 让“每条标准都有验收、每条验收都有结果行”可检查。
- **归档被当成事务做**：过 close 门 → `git mv` → ignore 镜像 → untracked 复核 → 失败回滚 → `--dry-run`/`--commit`，方向正确，比多数文档型 skill 强。
- **领域手册有真东西**：A→B→A' 交错、三档结局、fw-swap 3b/3c/3d、filter 虚标的教训，不是泛泛建议。
- **4.6.0 的方向对**：tasks 成为唯一台账、收口段机器门、status 显示收口列与项目 spec 状态，都是在补“执行期”的洞。

### 2.2 最危险的是什么

**门在验证形状，不在验证事实。** close 门能查出“少了 C 结果行”“C 引用了不存在的 S”，但查不出“C 结果是 ❌”“证据是假的”“实测 25 min 违反 ≤15 min”“项目 spec 只在正文提了一句 change 名”。这些恰好是归档前最需要确认的事实。于是出现最坏组合：**格式齐全 + 结论错误 + 归档成功**。

**第二危险的是交付链。** 本机安装副本是 4.6.0，但 `origin/main` 与 `gitee/main` 仍是 `ac46cee` / 3.4.4，本地领先 7 个提交；按 README 的 `curl ... install.sh` 安装，会拿到 3.4.4，并覆盖本机 4.6.0（有备份、不阻断）。评审结论再好，用户拿不到就等于没有。

---

## 3. P0：会让错误结论进入 archive

### P0-1 close 门放过 ❌：失败的 change 可以按“通过”归档

**证据**

- `tools/qwork-check.py:281-284`：判定只校验是否属于 `{✅, ❌, ⚠️}`；只有 `⚠️` 才要求 spec 有“阻塞收口”，`❌` 没有任何后续分支。
- `SCHEMA.md:136` 明确写：“不通过 → 回到 design.md / tasks.md 继续迭代，不归档。”
- 本轮在 4.6.0 复现（`/tmp/qw-final`）：把 `examples/doc-change` 的 C1 判定改成 `❌`，`qwork-check.py --close` 输出：

```
close: 0 error(s), 0 warning(s) -> PASS
exit=0
```

同一目录 `qwork-archive.py --dry-run` 显示 close 门 PASS；`qwork-status.py` 显示“可归档”。归档后 spec 顶部没有 `⚠️ 证伪`，与通过的 change 不可区分。

**为什么是 P0**

archive 是信任边界：下游会话会把 archive 里的 change 当作“已验证结论”复用。全 ❌ 的 change 以“通过”形态进入 archive，比没有记录更危险——它给了错误结论一个“已验收”的外观。

**修法**

close 只允许两种终态：

1. **通过**：所有 C 判定为 ✅，tasks 全勾（含收口段），证据可检。
2. **拒绝留档**：显式标记 `> ⚠️ 证伪，状态: 拒绝` + design `§证伪记录` + tasks 末行 `最终：❌ 未通过`；允许归档，但归档摘要必须打印“证伪/拒绝”。

混合 ✅/❌ 且无拒绝标记 → error；`⚠️` 阻塞必须同时有 spec 阻塞收口 + 用户确认留痕；archive 打印 `N ✅ / N ❌ / N ⚠️` 的判定摘要，让归档内容自描述。

**验收**

- 全 ✅ → close 0；
- 一条 ❌、无证伪标记 → close 非 0；
- 一条 ❌ + 完整证伪标记 → close 0，archive 摘要含“证伪”；
- 一条 ⚠️、无阻塞收口 → close 非 0；
- 一条 ⚠️ + 阻塞收口 + 确认留痕 → close 0。

---

### P0-2 证据链不校验：假 hash、假路径都能过门

**证据**

- `tools/qwork-check.py:233` 只用 `STATUS_LINE` 匹配 `- [x] ...`，close 只统计 `[ ]` 数量（`:250-254`），不解析箭头后的 hash/路径。
- `SKILL.md:98` 自己写：“`[x]` 无证据也算未完成”——工具没有消费这条规则。
- 圆桌实测：tasks 写 `- [x] 都做完了 → deadbee` 与 `- [x] 已复跑 → /no/such/evidence.txt`，close 仍 `0 error(s), 0 warning(s) -> PASS`；`git cat-file -t deadbee` 报 `fatal: Not a valid object name deadbee`。

**为什么是 P0**

如果 `[x]` 可以没有证据，或证据可以是任意字符串，那么 S/C 追踪、收口段、验收人全部退化为“写对格式”。这是自证自验，不是验收。

**修法**

定义三类可机检证据，`[x]` 至少满足一类：

1. **git 对象**：`→ commit <7-40 位 hash>`，用 `git cat-file -e <hash>^{commit}` 校验；短 hash 必须唯一可解析。
2. **仓内路径**：`→ 证据: <path>`，路径存在（文件/目录），且不允许 `<...>` 占位。
3. **用户确认**：`→ 用户确认: <who> <YYYY-MM-DD> <会话/消息 ref>`；这是外部锚点，不能由执行者单独伪造（见 §6 分歧）。

不满足的 `[x]` 不计入完成，close 报 error；`实测` 列为空/占位时判定不得为 ✅。

**验收**

假 hash、假路径、`<路径>` 占位、无证据的 `[x]` 各一条 → close 非 0；真 hash、真实文件、用户确认各一条 → close 0。

---

## 4. P1：会让下一步、协作或 repo 状态失真

### P1-1 archive `--commit` 越界提交，且 commit 失败不回滚

**证据**

- `tools/qwork-archive.py:9` 自述“`--commit` 只提交本次归档相关路径”；实现却：
  - `:192` `git add -A -- rel_old rel_new .gitignore`；`git mv` 后 `rel_old` 已不存在，实测 rc=128（`fatal: pathspec ... did not match any files`）。
  - `:194-197` 兜底 `git add -A -- 0_workbench .gitignore`——这是**常态路径**，不是异常路径。
  - `:200` `git commit -m` 不带 pathspec，提交整个暂存区。
  - `:275-276` commit 在 `:252-268` 的回滚 try 之外；`:270` 在 commit 之前就打印“✅ 已归档”。
- 本轮 4.6.0 复现：另一 change 的未提交 `tasks.md` 被卷进 `demo: 归档收口`；预暂存的 `src/app.py` 也会被带入。给 `.git/hooks/pre-commit` 加 `exit 1` 后，stdout 先打印“✅ 已归档”，随后 exit 1；change 已移入 archive、index 处于 R 重命名、没有回滚。

**为什么是 P1（接近 P0）**

它不会直接产生错误结论，但会破坏归档边界：把别的会话/别的 change 的 WIP 提交进历史，可能带入未审阅的代码或敏感信息；commit 失败后半状态无法重试，用户只能手工收拾。

**修法**

1. 删除 `fallback = ["0_workbench"]`；`git add` 只加**存在**的 `rel_new` 与确实变更的 `.gitignore`。
2. `git commit -- <允许路径>` 限定 pathspec；提交前打印暂存清单，断言暂存集 ⊆ 允许集。
3. 把 commit 纳入同一个 try/except；失败时回滚移动与 `.gitignore`；成功之后再打印“已归档”。
4. **明确项目级 spec/design 的收口改动怎么提交**：要么要求先单独提交，archive 只负责移动；要么把 `0_workbench/spec.md` / `0_workbench/design/` 放进显式允许集，并在提交前打印清单。二选一写进 docstring，不能再用目录级 fallback。

**验收**

- fixture 含另一个 change 的未提交改动 + 用户预暂存文件 → archive commit 后 `git show --name-only` 只含 `archive/demo` 与 `.gitignore`（或显式允许的 spec/design）。
- pre-commit `exit 1` → change 未移动、`.gitignore` 未改、无“✅ 已归档”。

---

### P1-2 status 与 close 不同源：面板说“可归档”，门说 FAIL

**证据**

- `tools/qwork-status.py:112-117` 的“可归档”只依赖 `missing_results`（check 里的 C 是否在验收结果有同名行）、收口段和项目 spec 记录，不校验 S→C 覆盖、C 引用合法性、判定值。
- 圆桌实测：`check.md` 的 C1 改成引用不存在的 `S9`，`qwork-status.py .` 仍输出“可归档 / 跑 qwork-archive”；同一目录 `qwork-check.py --close` 报 `ERROR check C1 引用了不存在的 spec「S9」`。判定全写 `OK` 时，status 仍“可归档”，check 报 4 条 error。

**为什么是 P1**

SKILL §5 让接手者先跑 status 当下一步指针；面板给出一个无法执行的动作，冲突被推到最贵的时点（归档）。三人小组的协作协议正建立在“可归档”这个信号上。

**修法**

在“任务全勾 + 收口完成”的终态，status 直接调用 `qwork-check.py --close --json`（同仓同 Python，子进程即可），用其 `errors` 决定状态：

- close exit 0 → “可归档”；
- close 非 0 → “待收口（close 门 N error）”+ 首条 error；
- 非终态仍用现有轻量状态机，不跑 close。

补一条回归：对同一 fixture，`status 说可归档 ⇔ close exit 0`。

---

### P1-3 legacy / 结构逃逸：删一列、改个标题就能免检

**三条实测路径**

1. **新 change 自称 legacy**：删 ID 列、删收口段 → `qwork-check.py:124/157` 判 legacy、`return None`，close PASS（3 warning）。
2. **只改 check 表头**：把 `| ID |` 改成 `| 检查项 |`，`check_ids` 变 `None`，`check_closure(tasks, mode, check_ids is None, f)`（`:246`）把“缺收口段”从 error 降为 warning → close PASS。change 其余部分仍是新格式，只改一个列名就绕过 4.6.0 的收口硬门。
3. **真 legacy 被硬拦**：README.md:121 与 CHANGELOG 4.5.0 都说“旧格式只报 WARNING”，但 `check_tasks` 对缺“验收结果”表仍 error（`qwork-check.py:267-269`），项目 spec 也直接 error；真实 pilot close 得 3 error，archive 默认拒绝。

**为什么是 P1**

legacy 既是逃生门（任何新 change 都能自称旧格式），又是陷阱（真旧 change 不能按 README 的预期归档）。pilot 就是后者：它是唯一真实 dogfood 现场，却被锁死。

**修法**

- **用显式标记判 legacy**，不用“缺结构”推断：spec 顶部 `> retroactive: <YYYY-MM-DD> <原因>` 才算 legacy；没有标记的新 change 缺 ID 列/收口段/接手须知 → error。
- legacy 标记只降级**格式类**检查（ID 列、S/C 覆盖、收口段），不降级“验收结果表存在”之外的事实检查；“旧格式只报 WARNING”要么改成准确表述，要么让验收结果表在 legacy 下也 warn。
- 补迁移清单：维度表 → S 行、check 章节 → C 表、tasks 补接手须知/验收结果/收口；`qwork-check --close` 打印“legacy（retroactive）：跳过了 N 项检查”，让用户知道降级了什么。
- archive 对 new change 默认 `--close` 即 strict；legacy 才允许 warning。

**验收**

- 新 change 删 ID 列/删收口段 → close 非 0；
- 只改 check 表头 → close 非 0；
- 真 legacy + `> retroactive` → close 0，且输出“跳过 N 项”；
- pilot 加标记 + 迁移后 → close 0。

---

### P1-4 规范与工具互相打架：照 SCHEMA 写反而失败

这是本轮最讽刺的一类问题：宪法自称定义“做成什么样”，它的示例却过不了自己的门。

| 冲突 | 证据 | 后果 |
|---|---|---|
| 判定 token | `SCHEMA.md:75` 要求 `❌ 未通过（证伪）`，`:82` 要求 `⚠️ 阻塞交付`；`tools/qwork-check.py:25` 的 `VERDICTS` 只接受精确 `✅/❌/⚠️`，`:281` 精确相等 | 照 SCHEMA 写 → `ERROR 验收结果 C1 判定必须是 ✅/❌/⚠️`；必须把后缀挪到“实测”列才能绕过 |
| 验收表格式 | `SCHEMA.md:113` 示例表头是 `| 维度 | 目标(spec) | 实测 | 判定 |`；`templates/tasks.md:49` 与 checker 要求 `| ID | ... |` 行 | 照 SCHEMA 写 → 4 error（`'吞吐'`/`'稳定性'` ID 非法 + C1/C2 无行），close FAIL |
| 项目 spec 记录 | `qwork-check.py:291-305` 只做全文裸子串 `if change.name not in read(pspec)`，却报“变更记录没有 X 行” | 正文提一句 `demo` 就 PASS；change 名 `fix` 命中 `prefix`；change 名 `demo` 命中 `demo2` |

**修法**

- 判定列改**前缀匹配** `^(✅|❌|⚠️)(\s+.+)?$`，后缀按 SCHEMA 词表校验（`未通过（证伪）` / `阻塞交付`）；或规范改为“判定列只放符号 + 新增‘处置’列”，并同步 §拒绝态/§阻塞收口。
- SCHEMA 示例改为 C 行（保留维度列），或 checker 接受维度行并按 S 映射；明确 **templates + checker 是工件格式唯一权威**，SCHEMA 只引用、不另举格式。
- 项目 spec 只在 `## 变更记录` 段内按表格行/词边界匹配（如 `| <date> | <name> |`），未命中给出应插入的行样板。
- 补一条“冷启动探针”：照 SCHEMA 原文逐字抄一遍 tasks 验收结果，要求 close PASS；照 templates 抄一遍，也要求 PASS。

---

### P1-5 验收数值不校验：25 min 对 ≤15 min 仍判 ✅

**证据**

- `tools/qwork-check.py:272-284` 只校验 ID、判定符号、⚠️ 阻塞收口，不比较“目标(spec)”与“实测”。
- 红队实测：`| C3 | S3: ≤15 min | 25 min | ✅ |` → close `0 error(s), 0 warning(s) -> PASS`。
- 方法角色另测：spec S3 目标改 `≤10 min`、check C3 仍 `≤15 min`、tasks 记 14 min ✅，close 仍 PASS——check 成了第二阈值源。

**为什么是 P1**

这比“check 阈值漂移”更直接：实测已经违反目标，仍标 ✅，门禁放行。归档的是自相矛盾的结论；S/C 追踪链在终点失效。

**修法**

- 对 `目标(spec)` 与 `实测` 做**可机械比较的简单解析**：`≤/≥/</>/区间/等式` + 数字/单位；实测不满足目标却判 ✅（或满足却判 ❌）→ error；无法解析的目标标“人工”并跳过。
- check 的判定口径只写“按 spec S3 目标判定”，不复制数值；黄金样例删掉重复阈值。
- 目标是“机械可判定的数值”才校验，不做通用语义判断；无法解析时明确“人工”，不假装机器验过。

**验收**

- 25 min vs ≤15 → error；
- 14 min vs ≤15 → 0；
- `3/3` vs `3/3` → 跳过或字符串相等；
- spec ≤10、check ≤15 → 提示阈值不一致（可先 warn，后 error）。

---

### P1-6 执行交接：tasks 既“只读”又“只写”，阻塞被当成“继续施工”

**证据**

- `SKILL.md:122` 同一句：“执行会话**只读四要素 + data/**（spec/design/tasks/check 全读、只读）”与“**只写 `tasks.md` 与 `data/`**”。tasks 同时被定为只读和可写。
- 真实 pilot 施工中两次改 check 判据（`506a963`、`d0e6170`），执行者回报“tasks.md 本次未触碰”；P4 阻塞仍是 `[ ]`，status 显示“施工中（剩 1）/继续施工”，dispatch 仍 PASS。
- `SKILL.md:91` 铁律“同一任务连续失败 3 次 → 停”；pilot 的 P4 按任务包做了 8 次“换假设取证”，两者冲突，派单方只能自造预算。
- `qwork-check.py:259` 把“派发前有 N 个未开始任务（正常）”记 warning；`--strict` 下 warning 即失败，新 change 的 `dispatch --strict` 必 FAIL。

**修法**

- 用**字段级权限表**写死：执行者可写 tasks 的勾选状态、证据、实测、判定、收口勾选；不可写目标、C ID、判据、范围；spec/design/check 只读。判据错误 → 停，回执附“偏差 + 建议 patch”，由规划会话改，执行者重读。
- 阻塞识别：`status`/`check` 识别行内 `BLOCKED`/`ENV` 注记，或强制执行者停前把 `[ ]` 改 `[!]`；status 输出“阻塞（等外部依赖）→ 走阻塞收口”，不再报“继续施工”。
- 熔断改按“同一动作/同一假设”计数；接手须知增“尝试预算”字段，并写明与铁律的优先级（任务包更严则从任务包）。
- dispatch 模式下“未开始任务”是正常态：改为 info，或 `--strict` 只对 error 生效；补测试：新 change `--dispatch --strict` exit 0。
- 两份黄金样例补回“不改 spec/design/check（判据错误→停并回报）”；checker 把“spec”与“不改”共现列为必含项。

---

### P1-7 分发链：7 笔未推送，用户装到的是 3.4.4

**证据**

- `git status -sb` → `## main...origin/main [ahead 7]`；`origin/main` 与 `gitee/main` 均为 `ac46cee`，`git show origin/main:SKILL.md` 仍是 `version: 3.4.4`；本机 `~/.dsh/skills/qwork` 是 4.6.0。
- README.md:13 的安装路径是 `curl ... gitee ... install.sh`；`install.sh:84-98` 在“本地版本高于源”分支只打印“开发版，覆盖安装”，随后照常 `mv` 换装远端旧版，不阻断。
- README.md:39-44 手动安装只 `cp SKILL.md / templates / references / SCHEMA.md / CHANGELOG.md`，漏 `tools/` 与 `examples/`；装完 §4/§6 的 check/archive/status 和黄金样例全部 no such file。
- `SKILL.md:3` description 148 字（R-07 限 100）；第 57 字截断在 `spec/design/tasks/c` 中间；`related_skills` 只有 adb-tftp、serial-tftp，缺 qwiki；正文不点名 qwiki，但 description 尾部写“把产出沉淀到知识库”，与 qwiki 触发词重叠。

**修法**

- **先修 P0/P1，再发 4.6.1，再推 gitee + GitHub 双远端**；不要原样推 4.6.0（它会把“全 ❌ 可 PASS”发给用户）。推送后跑三端 `install.sh --check`，确认 3.4.4 不再被当成最新。
- 手动安装块补 `cp -r tools` 与 `cp -r examples`；更彻底：该块直接引用 `install.sh` 的 `INSTALL_FILES/INSTALL_DIRS`，不出现第三份安装面。
- description 压到 ≤100 字（建议：`项目任务管理（workbench）：四要素 spec/design/tasks/check 驱动 change，验收→归档闭环，维护 0_workbench 进度。`）；`related_skills` 加 qwiki；§1 路由与 §4 第 4 步点名“知识库规则见 qwiki skill”。
- `scripts/hooks/pre-push:26` 名单加 `tools/|examples/`、去掉 `scripts/|assets/`，或直接从 `INSTALL_DIRS` 派生；加一条自检：INSTALL_DIRS 每项必须命中名单。

---

### P1-8 采用成本：小修与事故没有通道（需产品负责人拍板）

**证据**

- `SKILL.md:66`“四要素缺一不可”、`:22`“给出意图就按规范执行”；SKILL/SCHEMA/README 全文 grep 无“规模/轻量/不适用/hotfix”。
- 最小黄金样例 `examples/doc-change` 四件套 140 行，4.6.0 加收口段后 149 行；冷启动强制预读约 1.8 万字符（SKILL 8245 + SCHEMA §一~§三 6714 + templates 3098）。
- 唯一负向路径是 `SCHEMA.md:92` 的 retroactive：“不鼓励作为常规，但容忍”；线上事故时没人会先写 design，实际必然“先修后补”，补出来的四要素是事后叙述，close 只查格式仍判合格。
- 3-5 人场景：tasks 接手须知 9 项无负责人；status 无 owner 列；无 WIP 上限、无跨 change 依赖字段。

**为什么放在 P1 但标“需拍板”**

method/redteam 认为“轻量档”是产品取舍，不是规范 bug；pm 认为不做就会导致团队绕过 skill、退回手工 git。两者都对：**这不是“修 bug”，是“选择服务谁”**。如果 qwork 只服务单人或 AI 长任务，可以不做；如果要进 3-5 人团队，owner/WIP/依赖和小任务通道就是 P1。

**建议**

- 开单门槛（提案）：≥0.5 人日 / 动 ≥3 文件 / 有对外契约或实验裁决；门槛下走 lite 道：spec 三行 + tasks 一段 + check 一行证据，`qwork-check --lite` 只验 S/C 映射与证据。
- hotfix 道：spec 只填“现象/回滚条件/验收命令”三行即可动工，24h 内补 design/tasks 并标 `> hotfix`；status 对超期未回补标红且不计“已闭环”。
- owner/WIP：tasks 接手须知加“负责人”，change 加“阻塞于: <change>/<外部>”；status 增 owner 列；WIP 上限写进 SCHEMA。

---

## 5. P2：文档、维护与体验

| 项 | 证据 | 建议 |
|---|---|---|
| 缺失/未完成重复报 error | `qwork-check.py:325-327` 入口先报四文件缺失，`:113/:151/:242` 子检查再报；`:221` 收口未勾 + `:254` 总未完成重复 | 入口报一次，子检查见缺失直接返回；收口项从“未完成总数”扣除 |
| 接手须知 8/8/9 漂移 | SKILL:123 八问、README:105 八字段、SCHEMA:148 八项、templates/tasks.md 实为九条；checker 靠“回报”子串过关 | 以 templates + checker 字段表为唯一权威，定 9 项；checker 按行首字段名匹配 |
| 文档重复/体量 | SKILL 8245 + SCHEMA §一~§三 6714 + templates 3098 = 18057 字符；收口清单 SKILL:105 / SCHEMA:141 / README 三处复述 | 规则只在 SCHEMA 定义，SKILL 改指针；§2.6-2.7 下沉 references；目标 ~12k |
| pre-push 名单漏项 | `scripts/hooks/pre-push:26` 不含 tools/examples，含 scripts/assets | 从 INSTALL_DIRS 派生；加自检 |
| 探针停在 4.3.0 | `tests/probes.md` 结果表末行 4.3.0，4.4/4.5/4.6 未补 | 补三行；场景 1 增“S/C 编号与覆盖是否正确执行” |
| README 顺序/旧格式表述 | README:68 注释 spec→check→design→tasks，69-72 行按 spec/design/tasks/check 列；:121“旧格式只 WARNING”不实 | 按确认顺序列文件；改成准确表述 |
| SCHEMA 版本标注 | SCHEMA:5 “Last updated: 2026-11-14（v4.0.0…）” | 更新为 4.6.0/4.6.1 |
| 非 git 项目 | `qwork-archive.py:247` 硬要求 git；execution-handoff §六 说 workbench 可能不在 git 下 | 明确“archive 需要 git，非 git 保留 change/ 手工收口”，或实现无 git 移动方案 |
| 实验样例缺入口 | examples/experiment-change 无源码仓/构建命令；启动条件 md5 在 spec 中不存在 | 补仓路径、构建/烧录命令、产物路径；md5 写进 spec 或删条件 |
| 分析报告无落点 | 执行者只写 tasks/data；SCHEMA:155 产出物不许留 change/；data/ 只放原始产物 | 明确 data/report/ 可入库摘要，收口迁知识库 |
| 共享 spec/design 冲突 | 收口写 `0_workbench/spec.md` 与同一份 design；SKILL 并发防护只覆盖 change 目录 | archive 加收口串行提示/锁；changelog 改 per-change 段落 append |
| 知识沉淀强耦合 | 收口第 3 项依赖 qwiki 外部规则；qwork 不版本化 | 移出 close 硬校验，改 tasks 记“沉淀去向: <路径>/无需”；qwiki 在场时由 qwiki 触发 |
| 工具测试全手跑 | tests/tools.md 手跑，无退出码/JSON/提交内容断言 | pytest fixture：第二个 change + 预暂存文件 + hook 失败；断言 commit 内容/回滚 |

---

## 6. 角色分歧与裁决

多方评审的价值不在“一致同意”，而在把分歧摆出来。以下 6 组分歧按“是否影响归档可信度”裁决：

### 6.1 F1（spec/check 阈值复制）是 P0 还是 P1？

- **method** 判 P0：模板和样例复制了阈值，门禁不校验，改 spec 一处就产生冲突。
- **redteam** 判 P1：`templates/check.md:10` 只是占位符，examples 已标 C→S；docs/review-2026-11-14.md:33 已限定校验器只查形式与追踪。
- **裁决：P1。** 理由：它不是“错误结论直接进 archive”的最短路径（P0-1 才是），但确实会产生假 PASS；修法应从“删复制数值 + 加数值一致性校验”入手，而不是把例子全删。**不要把它降为 P2**，因为 25 min 对 ≤15 min 的假 PASS 已经实测。

### 6.2 legacy 应该“一律 error”还是“显式标记放行”？

- **redteam** 主张新 change 缺结构一律 error，否则任何 change 都能自称 legacy 逃逸。
- **method** 反对：pilot 这类存量会被一次性锁死，应保留 legacy 放行但绑 `> retroactive`。
- **裁决：显式标记放行。** 新 change 缺结构 → error；旧 change 加 `> retroactive` → 只降级格式类检查，并打印“跳过 N 项”。这样既不锁死 pilot，也不给新 change 零成本逃生门。

### 6.3 小任务轻量档 / hotfix 是“规范缺陷”还是“产品取舍”？

- **pm**：不做就会绕过，retroactive 会变成第一例合法绕过。
- **method/redteam**：SKILL:66“四要素缺一不可”是明确取舍，不是自相矛盾；1 小时小修要不要降档是采用率问题。
- **裁决：产品取舍，需负责人拍板。** 本报告给提案（门槛 + lite/hotfix），但不把它塞进 4.6.1 的 bug 修复；如果决定服务 3-5 人团队，则升为 P1。

### 6.4 “用户确认”怎么留痕才算数？

- **method**：加 `确认：<人> <日期> <原话>` 字段。
- **redteam**：这仍是执行者可自写的字符串，只是更长的咒语；真正锚点应是“归档由用户触发”或 commit trailer。
- **裁决：两者结合。** 短期要求 who/date/ref 字段（可审计性比现在好）；中期把“用户触发归档”或 commit trailer 作为外部锚点。**不要假装一个自写字段是密码学证明**；报告里明确它的强度边界。

### 6.5 status 要不要显示“通过/证伪/阻塞/废弃”四态？

- **method** 想要四态；**redteam** 指出 SCHEMA:72“归档不分成败”是显式设计，四态会与扁平归档冲突。
- **裁决：不改归档语义，改 status 读法。** status 读 spec 顶部标记，显示“已归档（通过/证伪/阻塞）”；archive 目录仍扁平，不新增状态机边。这样既保留“归档不分成败”的设计，又让面板不再把三种结局抹成“已归档”。

### 6.6 RT-01/02/05/06 是四条补丁还是一个数据模型改动？

- **method**：同一根因——验收表是自由文本，门只做正则形状检查；应合成“结构化验收表 + 与 spec 目标、S/C 引用、git 对象双向校验”一个根因项。
- **redteam**：分四条更利于排期。
- **裁决：报告按“现象”分条（便于修），实现按“一个数据模型”做（避免打四个补丁）。** 具体：验收表解析器 + 证据解析器 + 数值比较器 + 项目 spec changelog 解析器，四个函数共享一个“单元格/行”解析层。

---

## 7. 建议路线

### 7.1 4.6.1：只修 P0 + 归档/状态，1-2 天

| # | 改动 | 文件 | 验收 |
|---|---|---|---|
| 1 | close 拒绝 ❌ / 要求证伪标记 / ⚠️ 要求阻塞收口+确认 | `tools/qwork-check.py` | §3 P0-1 五条用例 |
| 2 | `[x]` 证据三类可机检；占位/假 hash/假路径 → error | `tools/qwork-check.py` | §3 P0-2 用例 |
| 3 | archive 删 fallback、pathspec commit、commit 入事务、成功后再打印 | `tools/qwork-archive.py` | 越界/回滚两条 fixture |
| 4 | status 终态调用 close --json；“可归档”⇔ close 0 | `tools/qwork-status.py` | status↔close 一致性矩阵 |
| 5 | SCHEMA 判定 token / 验收表格式 / 项目 spec changelog 段 | `SCHEMA.md`、`tools/qwork-check.py` | 照 SCHEMA 抄一遍能 PASS |
| 6 | legacy 显式 `> retroactive`；新 change 缺结构 error | `tools/qwork-check.py`、`SCHEMA.md` | 新 change 逃逸用例 + pilot 迁移 |

### 7.2 4.7.0：P1 执行/分发，约 1 周

- 字段级执行权限表 + 阻塞识别 + 熔断/尝试预算 + dispatch `--strict` 正常态。
- description ≤100、related_skills 加 qwiki、手动安装补 tools/examples。
- 修 P1-8 的拍板项（lite/hotfix/owner）；若决定不做，在 README 写明“不适用场景”，别让用户自己猜。
- 补 pytest：check/status/archive 三件套 + 负向 fixture。

### 7.3 4.8.0：P2 文档与维护，持续

- 去重、压到 ~12k 强制面；pre-push 从 INSTALL_DIRS 派生；probes 补 4.4/4.5/4.6；SCHEMA 版本/README 顺序；非 git 边界；实验样例入口；分析报告落点；共享 spec/design 冲突；知识沉淀软耦合。

### 7.4 发布门（每次发版）

1. `python3 -m py_compile tools/*.py`；
2. pytest（新增）全绿；
3. `skill-lint` 0 真 FAIL（先修 R-02/R-14 假红，或让 lint 支持 `INSTALL_FILES/INSTALL_DIRS`）；
4. `tests/probes.md` 三场景（新建/收口/改需求）在当版重跑；
5. `install.sh --check` 对 dsh / hermes / claude 三端一致；
6. **推 gitee + GitHub 双远端**，再核对 `git show origin/main:SKILL.md` 的 version。

---

## 8. 不建议做的事

1. **不要盲追 skill-lint 的 3 FAIL。** R-02（`templates/*.md` 未被反引号引用）与 R-14（COPY_DIRS/COPY_SCRIPTS 没覆盖）是假红：qwork 用 `INSTALL_FILES/INSTALL_DIRS`，SKILL.md:35 用通配引用。先修 lint 或加兼容变量，别为了变绿去改安装面。
2. **不要把“语义质量”塞进 checker。** 论证是否充分、实验设计是否合理，机器判不了；checker 只做路径存在、hash 可解析、数值比较、表格位置这类机械事实。
3. **不要把所有 legacy 缺结构一律 error。** pilot 会被锁死；用 `> retroactive` 标记 + 迁移清单。
4. **不要保留 archive 的目录级 fallback。** “容错”的代价是把别人的 WIP 提交进历史；宁失败，不放宽范围。
5. **不要把自写的“用户确认”当成证明。** 它是审计线索，不是外部锚点；真正锚点应在执行者控制域之外。
6. **不要给 check 再立一套阈值。** spec 是唯一阈值源；check 只引用 S ID，不复制数字。

---

## 9. 复现证据

以下均在 4.6.0（`5f99296`）上跑过；fixture 在 `/tmp/qw-*`。

### 9.1 全 ❌ 仍 PASS

```
$ cp -r examples/doc-change /tmp/qw-final/0_workbench/change/demo
$ # 把 C1 判定改成 ❌，补 0_workbench/spec.md 的 demo 变更记录行
$ python3 tools/qwork-check.py /tmp/qw-final/0_workbench/change/demo --close
close: 0 error(s), 0 warning(s) -> PASS
```

### 9.2 按 SCHEMA 写证伪反而 FAIL

```
$ # 判定改成 "❌ 未通过（证伪）"
$ python3 tools/qwork-check.py ... --close
ERROR   验收结果 C1 判定必须是 ✅/❌/⚠️（当前 '❌ 未通过（证伪）'）
close: 1 error(s), 0 warning(s) -> FAIL
```

### 9.3 archive 越界提交

```
$ # 另一个 change 的 tasks.md 有未提交改动
$ python3 tools/qwork-archive.py 0_workbench/change/demo --commit
$ git log -1 --name-only
... 0_workbench/change/other/tasks.md
```

### 9.4 commit 失败不回滚

```
$ printf '#!/bin/sh\nexit 1\n' > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
$ python3 tools/qwork-archive.py 0_workbench/change/demo --commit
✅ 已归档：0_workbench/change/demo → 0_workbench/archive/demo
❌ 命令失败：git -C ... commit
$ # change 已消失、archive/demo 已就位、index 处于 R 重命名
```

### 9.5 status 说可归档、close 说 FAIL

```
$ # check.md 的 C1 改成引用不存在的 S9
$ python3 tools/qwork-status.py .
... 状态：可归档 / 跑 qwork-archive
$ python3 tools/qwork-check.py . --close
ERROR   check C1 引用了不存在的 spec「S9」
```

### 9.6 dispatch --strict 对新 change 必失败

```
$ python3 tools/qwork-check.py <new-change> --dispatch --strict
WARNING 派发前有 1 个未开始任务（正常，收口时必须清零）
FAIL
```

---

## 10. 结论

qwork 的方法论骨架值得保留：四要素、S/C 追踪、证伪可归档、收口段、归档事务，都是真实项目里长出来的。**它现在的问题不是“规则太少”，而是“规则给的保证超过了工具能兑现的范围”**：close 说 PASS，但可能验收全 ❌；status 说可归档，但 close 会 FAIL；archive 说只提交本次归档，但实际提交整个 0_workbench。

修完 P0-1/P0-2 和 P1-1/P1-2，qwork 就从“看起来可靠”变成“门禁可信”；再修 P1-3/P1-4/P1-5/P1-6，执行者才能按文档不踩坑；最后处理 P1-7/P1-8，成果才能到达用户、团队才愿意用。

**下一步建议**：按 §7.1 做 4.6.1（P0 + archive/status），补 pytest 负向用例；4.6.1 通过发布门后再推双远端。若只想先要一个最小 patch，优先 P0-1（close 拒绝 ❌）与 P1-1（archive 删 fallback）——这两条直接决定 archive 里的东西能不能信。
