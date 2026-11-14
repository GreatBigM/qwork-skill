# Changelog

## 4.9.0 (2026-11-14)

### Added

- **项目约束机器门**：项目级 `0_workbench/spec.md` 可写 `## 约束表`（ID/指标/上限/单位/条件）；change spec 必须写 `## 项目约束核对`，逐条列 K 并填 `满足/不适用/需变更`。`qwork-check` 在 dispatch/close 校验：K 必须存在且不重复、每个 K 都要核对；`满足` 仅在 K 的单位出现在 S 目标时按首个数值与上限比较，相对目标/单位不一致/次数类只发 INFO（不阻塞 strict）；`需变更` 必须带 `用户确认: [用户] YYYY-MM-DD`。冲突两条路：永久改约束（`满足` 引用新值）或一次性例外（`需变更` + 确认）。次数类约束的「条件」必须写计数基准，为空/无基准词直接 error；机器抓测量口径的 `N 次` 与上限比较，`不适用` 与次数矛盾也报错。
- **GitHub Actions CI**：`.github/workflows/ci.yml` 跑 pytest、两份黄金样例 `--close`、`publish-check.py`、`git diff --check`。
- `tests/test_tools.py` 增 6 项（strict 隐含日志、约束冲突/通过、缺核对段、需变更未确认、单位不一致告警），`46 passed`。

### Changed

- `--close --strict` 现在隐含 `--require-logs`：每个「自动」C 必须有 `data/check-<C>.log` 且含 `exit=0`。`--require-logs` 仍可单独使用；默认（非 strict）行为不变。
- SKILL 19.8KB/156 行 → 16.8KB/139 行：去掉未解析的 `category`/`metadata.agent.triggers`/`related_skills`，压缩重复的操作说明，细节继续由 SCHEMA、templates 与 references 承载。
- SCHEMA §五增加「约束表」格式与核对段示例；`templates/spec.md` 增加「项目约束核对」段；README 更新 strict/约束门说明。
- `install.sh --check` 忽略 `__pycache__`、`*.pyc`、`.pytest_cache`，跑完测试后不再误报安装漂移。
- SKILL 补：非 git 仓的证据/归档降级；项目骨架缺失（含空 `design/`、无「变更记录」）先补；tasks 开单即建含「收口」段的完整骨架；项目级约束改动单独提交；`--strict` 日志的 `exit=0` 行格式。
- 接手须知数量统一为「10 项」；约束核对「说明」必填且不能是占位符。
- `qwork-check --dispatch` 提前 warning 项目骨架缺口（`design/` 空、项目 spec 缺「变更记录」），不再等到 close 才暴露。
- 新增 `INFO` 级别：相对目标/单位不一致/次数类只提示，不阻塞 `--strict`；避免「合法满足约束却永远过不了 strict」。
- 接手须知仍含 `<...>` 占位符直接 error；`experiment-playbook` 增加「先过项目约束」一节。
- 版本 4.8.3 → 4.9.0

## 4.8.3 (2026-11-14)

### Fixed

- **测量口径唯一归属 spec**：SKILL §2.7、SCHEMA §四边界明确工具/参数/环境/采样/对照序列写进 spec「测量口径」，check 只写步骤/命令并引用 `spec Sx`；examples 去除重复的 A→B→A' 序列与 `check-links.sh` 命令。
- **项目级 spec 升为上位约束**：change spec 不得静默突破项目级持久约束/已知天花板；确需变更须用户批准并更新项目 spec 变更记录，未裁决不得 close/archive。
- **doc 样例 C4 可追溯**：新增 S4「重复执行稳定」，C4 改挂 S4；tasks 验收结果与测试数据同步，消除「C4 挂 S1 但 S1 无此维度」。
- **design 观测点边界**：doc design 改为「无额外观测点」；experiment design 注明观测点仅用于定位，验收口径见 check。
- **SCHEMA 表述**：design 吸收改为「评估是否需要新增/更新项目级 spec 约束」；小任务写清「3 个施工任务 + 收口段 3 项」。
- `publish-check.py` 跳过 `.pytest_cache` / `.mypy_cache` / `.ruff_cache`；`.gitignore` 同步。
- 版本 4.8.2 → 4.8.3

## 4.8.2 (2026-11-14)

### Changed

- SKILL/SCHEMA 增加“小任务（同构轻量）”规则：单 S/单 C/3 任务仍走同一四要素与同一 close/archive 门禁；≤2 个非 workbench 文件、≤0.5 人日、不改阈值/口径、不跨 change。超限收口前升级，不设 lite 目录/参数/第二套门禁。
- README 标注本机 v4.8.2 与远端 3.4.4 的差异，本机安装用 `--local`。
- 工具与测试未改，沿用 `35 passed`。

## 4.8.1 (2026-11-14)

### Added

- `qwork-check --close --require-logs`：每个「自动」C 必须有 `change/data/check-<C>.log`，且日志中 `exit=0`；缺失或失败不能收口。默认不开启，团队可自行选择强制。
- `tests/test_tools.py` 增 2 项（缺日志/日志通过），`35 passed`。
- 版本 4.8.0 → 4.8.1

## 4.8.0 (2026-11-14)

### Added

- **可选执行器 `tools/qwork-run.py`**：解析 check.md 的验收表，只执行「自动」行中反引号命令，stdout/stderr/退出码落 `change/data/check-<C>.log`；支持 `--dry-run`、`--only C1,C2`、`--timeout`。command 失败/超时退出 1；不修改 tasks/check，不替代 `qwork-check --close`。
- `tests/test_tools.py` 增 2 项（自动项成功落日志 / 失败退出 1），`33 passed`。
- 版本 4.7.3 → 4.8.0

## 4.7.3 (2026-11-14)

### Added

- **WIP 上限**：`qwork-status` 读 `QWORK_WIP_LIMIT` 或 `0_workbench/qwork.conf` 的 `wip_limit=`（0/缺省不限），输出 `WIP: N/limit`，超限提示先收口/归档；`--strict` 超限退出 1。JSON 增加 `wip {limit, active, over}`。
- `tests/test_tools.py` 增 `test_status_wip_limit_and_strict`，共 `31 passed`。
- 版本 4.7.2 → 4.7.3

## 4.7.2 (2026-11-14)

### Added

- **负责人（owner）**：`tasks.md` 接手须知新增 `- 负责人：<name>`；`qwork-status --json` 输出 `owner`，人类表格不变。缺负责人只 WARNING，不阻塞开工，兼容存量 change。
- 模板/两份黄金样例补负责人；`tests/test_tools.py` 增 `test_status_reads_owner`，共 `30 passed`。
- 版本 4.7.1 → 4.7.2

## 4.7.1 (2026-11-14)

### Fixed

- **阈值单一来源**：check「判定口径」含 `≤/≥/</>/×N` 等数值比较/倍数时 FAIL（legacy 只警告），强制写「按 spec Sx 判定」，避免 spec/check 双阈值漂移。
- **实测对 spec**：tasks 的 ✅ 实测除对比任务行目标外，也按 C→S 对比 spec 目标；spec 收紧而 tasks 仍用旧值时 FAIL。
- **变更记录完整行**：项目级 spec 的 change 行必须日期/change/摘要三格非空，只有 change 名或空摘要 FAIL。
- `tests/test_tools.py` 增 3 项（check 数值副本、变更记录空摘要、实测对 spec 目标），`29 passed`。
- 版本 4.7.0 → 4.7.1

## 4.7.0 (2026-11-14)

### Docs（冷启动补丁）

- **外部代码仓**：§0 增「目标代码/环境不在当前仓」分支——接手须记外部路径/分支/commit/获取方式；外部 commit 不作本仓证据，证据用复制进 `data/` 的日志或用户确认。
- **提交范围**：开单/阶段提交只 add 本 change 与本次改动文件，禁止 `git add -A`；他人 dirty 先问归属，`data/` 默认 ignore。
- **环境缺失三分**：命令跑不动（127/ENOENT/权限/设备不在）= 环境缺失，不是实测不满足，也不是证伪；自动检查必须留 `data/` 日志，`qwork-check` 只验记录不执行命令。
- **改需求同步**：上限未知先立 P0 测量，不得直接判可行；复用旧结论前复核证据与环境；check 判定口径/tasks 验收表必须同步，变更记录不能只有表头。
- **SCHEMA**：同步「最终：」/证据/执行边界说明。

### Tests

- 工具无改动，沿用 4.6.4 的 `26 passed`；冷启动探针未复跑，`tests/probes.md` 4.7.0 行标「未复跑（文档）」。

- 版本 4.6.4 → 4.7.0

## 4.6.4 (2026-11-14)

### Fixed（证据与骨架）

- **完成证据加硬**：`→ 证据: <path>` 指向空文件不再放行；`→ 证据: 用户确认` 必须带 `YYYY-MM-DD`；`[x]` 同行含 `BLOCKED_*`/等待/未验证即 FAIL，堵住“勾完成但写着阻塞”的自相矛盾。
- **项目骨架**：新格式 change 归档前要求项目级 `0_workbench/design/` 存在且非空（legacy 只警告）；`design.md` 为空也 FAIL。
- **最终结论**：有 `[!]` 阻塞任务或有 ⚠️ 阻塞交付时，「最终：」必须是 `⚠️ 阻塞交付`，不得写通过；全 ✅ 但写“通过（P1 未验证）”也 FAIL。
- **check 占位符**：检查方法含 `<...>` 直接 FAIL，不再让 `<命令>` 过 dispatch。

### Tests

- `tests/test_tools.py` 增加 9 项（空证据、`[x]` 阻塞/等待矛盾、空 design、项目 design 缺失/为空、混合最终、阻塞任务写通过、占位检查方法），`26 passed`；`tests/tools.md` 补 4.6.4 记录。
- `tests/probes.md` 4.6.4 行标「待复跑」。

- 版本 4.6.3 → 4.6.4

## 4.6.3 (2026-11-14)

### Fixed（收口一致性）

- **tasks 最终结论**：`--close` 要求 `最终：` 行存在且与验收判定一致（无 ❌ 写通过，有 ❌ 写 `❌ 未通过`）；缺行或「全 ✅ 却写未通过」直接 FAIL。堵住“勾选/判定/总结三份记录互相矛盾”的归档路径。
- **验收标题兼容 `#`**：`section()` 现在识别 `#`/`##` 标题，`# 验收`、`# 验收项` 不再被当成缺失；标题按精确/前缀匹配，避免把 change 名前缀里的“验收”误判为小节。
- **archive `--dry-run` 先出计划**：close 门失败时也打印项目根/归档路径/git 跟踪/ignore 计划，再打印门禁 error，便于先看“会做什么”再修。

### Tests

- `tests/test_tools.py` 增加最终结论缺失/矛盾、`#` 验收标题、dry-run 失败仍出计划 4 项，`17 passed`；`tests/tools.md` 补 4.6.3 记录。
- `tests/probes.md` 4.6.3 行标「待复跑」，不冒充通过。

- 版本 4.6.2 → 4.6.3

## 4.6.2 (2026-11-14)

### Added（阻塞提示）

- **status 识别未勾任务里的阻塞标记**：`[ ]` 同行写 `BLOCKED_*`、`阻塞原因：`、`等待外部`、`等待依赖`、`无法继续` 时，不再显示「施工中」，改为「阻塞（待确认 N）」+「改 [!] 并走阻塞收口」；`--json` 增加 `blocked_hints` 与 `blocked_hint_tasks`。只提示，不自动改状态。
- SKILL §3 / SCHEMA §三 / README 工具段补对应说明。

### Tests

- `tests/test_tools.py` 增加 status/close 阻塞提示回归，`13 passed`；`tests/tools.md` 补 4.6.2 记录。

- 版本 4.6.1 → 4.6.2

本文件记录版本历史。版本号定义在 SKILL.md frontmatter 的 `version` 字段（单一真相源）。

## 4.6.1 (2026-11-14)

### Fixed（门禁可信度与归档边界）

- **close 不再放过失败验收**：验收结果含 `❌` 必须走证伪留档（spec 顶部 `> ⚠️ 证伪，状态: 拒绝` + design §证伪记录 + tasks `最终：❌ 未通过`），否则 error；`⚠️` 必须走阻塞收口并带用户确认日期。
- **`[x]` 证据机检**：每条 `[x]` 必须带 `→`，后接 `用户确认: 用户 YYYY-MM-DD` / `证据: <存在的路径>` / `commit <存在的 hash>` 三选一；占位、假 hash、假路径、空证据均 error。`--close` 对全部施工任务与收口段逐条检查。
- **实测 vs 目标**：`✅` 的「实测」不能为空或占位，可解析的数值/单位会与 spec 目标比较（如 `≤15 min` vs `25 min` 报错）。
- **证伪/阻塞/legacy**：`❌ 未通过（证伪）`、`⚠️ 阻塞交付` 按 SCHEMA 接受；legacy 只认 spec 顶部 `> retroactive` 标记，不再靠缺表头推断，删表头不能绕过。
- **项目级 spec**：只在「## 变更记录」段内按表格行匹配 change 名（独立单元格），正文提及不算；示例改为表行。
- **archive**：`--commit` 只提交 `archive/<name>` + 变更过的 `.gitignore`，删目录级 fallback；commit 移入事务，失败回滚移动/`.gitignore`/暂存区；成功提示不再先于 commit 打印。
- **status**：终态改为调用 close 门，门不过显示 `待收口（close 门 N error）`，不再自报「可归档」。
- **check**：修复入口与各检查器重复报「文件缺失」；`--dispatch` 不再把「未开始任务」当 warning，新 change 的 `--dispatch --strict` 可通过。
- **examples/templates**：黄金样例补 `data/evidence.md` 与 `→` 证据；check 判定口径去掉 spec 阈值副本；SCHEMA 验收表改为 `ID` 表头、项目 spec changelog 改为表行。

### Tests

- 新增 `tests/test_tools.py`（pytest，11 项）：close 证据/❌/数值比较/项目 spec 表行、status 调门、dispatch strict、archive 提交边界与回滚；`python3 -m pytest -q tests/test_tools.py` → 11 passed。
- `tests/tools.md` 补 4.6.1 记录；`tests/probes.md` 标注冷启动探针待复跑（4.6.1 门禁语义已变）。

- 版本 4.6.0 → 4.6.1

## 4.6.0 (2026-11-14)

### Changed（tasks 成为执行唯一台账）

- **tasks = 执行唯一台账**：进度、阶段结论、commit、测试数据、验收结果、收口动作都记录在 tasks；**tasks 全勾（含收口段）= change 完结**，归档只是移动，不再把收口动作留在 tasks 之外。
- **tasks 新增「收口」段**（模板/样例）：design 吸收、项目级 spec 复审+changelog、产出落库/确认无需三项；每项有判据与证据，全勾才算完结。
- **每阶段加「阶段结论」**：阶段末记结果/偏差/决定，执行中的判断不丢。
- `qwork-check.py --dispatch/--close`：新增收口段检查（新格式缺段或收口段有 `[ ]` 判 FAIL；`--dispatch` 也要求先规划收口段；legacy 只 WARNING）。
- `qwork-status.py`：新增「收口」列与状态——缺收口段 / 收口剩 N 项；tasks 全勾但收口未完成不再显示「可归档」；可归档前还会核对项目级 `spec.md` 是否记了该 change（`project_spec_logged`）。
- SKILL §4/§5、SCHEMA §一/§三、README、troubleshooting 同步；两份黄金样例补阶段结论与收口段。
- **Fixed**：`qwork-archive --commit` 在项目没有 `.gitignore` 时不再因 `git add .gitignore` 失败；无镜像规则时下一步命令不再提示 `.gitignore`。

- 版本 4.5.0 → 4.6.0

## 4.5.0 (2026-11-14)

### Added（归档与总览）

- **`tools/qwork-archive.py`**：默认先跑 close 门；被跟踪用 `git mv`，否则普通移动；把 `.gitignore` 的 `change/` 规则镜像到 `archive/`，并复核 `data/**` 不因路径变化变 untracked；失败回滚；`--dry-run` 预演、`--commit` 提交、`--force` 跳过门。
- **`tools/qwork-status.py`**：扫 `change/` 与 `archive/`，输出四要素、任务完成度、C 覆盖、状态与下一步；`--json`。
- SKILL §4/§5/§7、SCHEMA §三、README 接入两个命令；README 工具段扩为 check/archive/status。

- 版本 4.4.0 → 4.5.0

## 4.4.0 (2026-11-14)

### Added（追踪与门禁）

- **检查项稳定 ID**：spec 成功标准表加 `ID（S1…）`；check 改为 `C1…` 表（ID / spec / 检查方法 / 判定口径 / 类型）；tasks「验收结果」按 C 行。规则：每个 S 至少一个 C，每个 C 必须有结果行。
- **`tools/qwork-check.py`**：`--dispatch` / `--close` / `--strict` / `--json`。机器检查四文件、ID 唯一性、S/C 覆盖、接手须知八字段、未完成任务、阻塞收口、C 结果行、项目级 spec changelog；旧格式只报 WARNING。
- **安装面**：`tools/` 随技能下发，`install.sh` 清单与 `--check` 同步。
- 模板与两份黄金样例改为 ID 格式；README 增加「校验门」用法。

- 版本 4.3.0 → 4.4.0

## 4.3.0 (2026-11-14)

### Added（方法论闭环 + 黄金样例 + 回归清单）

- **who / when 进工件**：tasks 接手须知新增「决策权 / 启动条件 / 停止与重规划条件」；check 新增「验收人（自验/独立）」；spec 新增可选的「为什么现在做」。
- **派发八问重排**：⑥ 合并「禁止项 + 谁拍板」，⑦ 改为「启动/停止条件」，仍为八问。
- **黄金样例**：`examples/doc-change`（文档类）与 `examples/experiment-change`（实验类）两份填满的 change；`examples/` 纳入安装面。
- **探针回归清单**：`tests/probes.md` 固化三个冷启动场景与评分口径。
- **评审汇总**：`docs/review-2026-11-14.md`。
- **闭环字面冲突修复**：收口清单①改为「tasks 收口（`[x]` 有证据 / 经确认的 `[!]` 视同收口）」；状态符号、流转图、阻塞收口三处对齐，并补「证伪」终点。

- 版本 4.2.0 → 4.3.0

## 4.2.0 (2026-11-14)

### Changed（四要素定位收敛为用户口径）

- **四要素的单一回答固定为**：spec = 做成什么样；design = 怎么做；tasks = 怎么组织；check = 怎么验收。
- design 的「为什么这么做」并入 design（决策理由），不再单独作为回答；tasks 的「谁做什么」并入「怎么组织」（阶段/顺序/粒度/归属/进度）。
- SKILL 的四要素表增加「定位」列（合同 / 图纸 / 路书 / 量具）与「交接保证」；SCHEMA 表头、README 同步。

- 版本 4.1.0 → 4.2.0

## 4.1.0 (2026-11-14)

### Added（编排 / 交接闭环）

- **四要素定义收口**：spec = 做成什么样 + 为什么做；design = 为什么这么做 + 怎么做；tasks = 谁做什么 + 做到哪；check = 怎么检查 + 阈值多少。四者是四个问题的答案，缺一即闭环断开（SKILL / SCHEMA / README 同步）。
- **修正执行授权**：执行会话由「只读 tasks」改为「只读四要素 + `data/`，只写 `tasks.md` 与 `data/`」——原规则与「测试方法见 check.md」自相矛盾，执行者必然破例。
- **派发就绪自检（八问）**：派单前逐条确认（读什么/第一步/完成判据/基线口径/环境/禁止项/阻塞回报/交付物）；任一答成「在之前的对话里」即未冻结，先补再派。
- **tasks 模板新增「接手须知」**：必读、环境前置、绝对禁止、完成判据、阻塞回报、交付物；任务行加「判据」字段。
- **执行回执格式**：完成 / 证据 / 偏差 / 未决 / 下一步 / 工作区终态；补「冷启动演练」方法。

- 版本 4.0.0 → 4.1.0

## 4.0.0 (2026-11-14)

### Changed（结构性重构：通用流程与领域手册分离 + 跨技能契约对齐）

- **SKILL.md 瘦身 12.4k → 4.8k 字符（-61%）**：驱动 CONFIG A/B、固件换版、长测等约 1/3 篇幅移入 `references/experiment-playbook.md`；对话分离、子代理、核验三查、并发防护移入 `references/execution-handoff.md`。SKILL 只留操作流程 + 指针。
- **新增 §0 定位与开工自检**：项目根 / `0_workbench/` 查找规则、缺失时按 SCHEMA §一 建树、开工四查——此前「在哪建 change」无规则。
- **DSH 适配**：删 `execute_code`、`~/.hermes/cache/...`、`ps aux | grep hermes` 等外部运行时残留；子代理/后台作业改平台中性表述并给 DSH 工具映射（`subagent`、`bash` run_in_background + `job_output`）。
- **知识沉淀衔接去耦（SCHEMA §四）**：只保留产出物交接与边界（产出物不进 change 目录、写清来源 change、闭环必检），不再复述知识库侧的目录/命名/登记规则——规则归知识库侧，避免两套口径漂移。
- **`change/data/` 纳入宪法**：§一/§二 定义原始产物落点；数字结论回填 tasks。
- **`[!]` 阻塞态定义**：未解除不得归档；补 change 命名约定（kebab-case、不带日期、先查重）。
- **模板去假状态**：tasks 模板不再预置 `[x]` 与 ✅/❌ 结论；check 模板按验收维度自由分组；design 模板补「观测点」节。
- **反模式表更新**：素材 YAML 头、模板预置勾选、结论写 check、占位符当命令、假收口。
- **闭环可执行性修复（首轮功能探针驱动）**：收口清单①改为「tasks 全 `[x]` 且无未解除 `[!]`」；新增阻塞收口；补 `git mv`/ignore 迁移、半残 workbench 补齐、`AGENTS.md` 必读、基线未测的相对目标与回填规则、测量口径、知识库缺失兜底、改需求同步链。
- **二轮探针修复**：开单即提交；change 级变更记录与「失效任务重开」规则；底线/测量口径兜底；design 未勘察项标记；阻塞态 `[ ]→[!]` 转换与自查；check 可执行性要求；`git mv` 前置建 archive 与提交信息；存量 `data/` 不强制迁出；§七 仅用于从零初始化；实验裁决阈值归 spec。
- **三轮探针收尾**：design 文档命名（`<主题>-design.md`）、空白骨架的项目 spec 兜底、目标上调的可行性/底线校验、知识库技能发现措辞。

### Added（安装与维护机制）

- `install.sh` 新增 `--local`（用当前 checkout 安装/验证，不克隆远端）与 `--check`（对比安装副本与源清单，非 0 退出即漂移）。
- `install.sh` 用 `INSTALL_FILES`/`INSTALL_DIRS` 单一清单驱动拷贝与校验；新增 `references/local/` 约定：升级时保留本地实践文件。
- `.gitignore` 排除 `references/local/`。
- README 更新：安装命令、本机扩展、仓库结构、快速上手。

- 版本 3.4.4 → 4.0.0

## 3.4.4 (2026-11-09)

### Changed
- **安装目标调整**：新增 `dsh`（DeepSeek Harness，`~/.dsh/skills`，按 `dsh` 命令探测）；**移除 `pi`**（不再支持）。

## 3.4.3 (2026-11-09)

### Changed
- **发布仓更名 `workbench-skill` → `qwork-skill`**（Gitee / GitHub 双远端已改）：`install.sh` 的 `REPO_URL`、README 的 clone / raw 下载地址同步更新。**旧安装命令失效**，请改用 `https://gitee.com/GreatBigM/qwork-skill/raw/main/install.sh`。

## 3.4.2 (2026-11-09)

### Changed
- **技能更名 `workbench-workflow` → `qwork`**（与 `qwiki` 同族命名；`0_workbench/` 目录结构与「workbench」概念词不变）。安装路径随之变为 `<tool>/skills/qwork/`。

## 3.4.1 (2026-10-25)

### Added

- **长测 / 长等待纪律**：只留一个权威 job（多 change 共用一轮长测 + 证据映射表）；末片 sleep 对齐已知终点（3×1740 + 尾片 1700 越过 2h ⇒ 多等 7.5min）；判完成靠 `SOAK_DONE`/`Written: OK`/`partition PASSED` 标记而非时长；长任务走 background + notify

## 3.3.7 (2026-10-15)

### Changed
- pre-push 的 CHANGELOG 同步名单注释补 `assets/`（与正则实际枚举一致）——九仓该文件文本归一

- 版本 3.3.6 → 3.3.7

## 3.3.6 (2026-10-15)

### Fixed（审查项落地：发布件残留 + 文档口径矛盾）

- **发布件正文残留厂商名 3 处（P0：随 install.sh 一并下发且仓库公开 ⇒ 已在漏）**：SKILL.md「驱动 CONFIG A/B 试验方法论」一节里谱系补丁场景与「同型号多机辨识」示例含厂商名 → 换泛化表述（「同厂商谱系补丁双分支同步」/「同厂商补丁」/「hostname 相同」），语义不变
- **SKILL.md 新建 change 流程的四要素顺序与宪法相反**（写 spec → design → check）→ 改回 `SCHEMA.md` §二确认顺序 spec → check → design → tasks（tasks 边做边填）
- **README 手动复制块漏 CHANGELOG.md** → 与 `install.sh` 实际拷贝面（SKILL.md / SCHEMA.md / templates / references / CHANGELOG.md）逐项对齐
- **README 仓库结构块漏 CHANGELOG.md** → 补一行
- **README 铁律把阈值写进 check**：正例「iperf3 TCP RX ≥ 80Mbps」与 `SCHEMA.md` §二边界约定（check 只给方法、不含结论、不重定标准、不得出现 spec 之外的门槛）冲突 → 改为「≥ <spec 标准值>」，注明阈值一律引自 spec 成功标准表；SKILL.md「check.md 写法」示例同源收敛
- **CHANGELOG 说明行（版本号单一真相源）夹在两个版本条目之间** → 移到 H1 之后
- **历史条目术语双轨（加注，不删历史）**：1.0.0「templates 六件套」加注「（模板已收敛为四件套，见 3.3.5）」；3.0.0「产出物入知识库 references/」加注「（目录名后改为 resource/）」；同族残留 SKILL.md 触发条件「写 references 产出」→「写 resource/ 产出」（旧目录名漂移的最后一处）
- 版本 3.3.5 → 3.3.6

## 3.3.5 (2026-10-15)

### Fixed（发布件脱敏收尾 + 文档修复）

- **SKILL.md 正文真代号占位化**：换文件类实验两处项目代号 → `<项目A>`；本条 3.3.4 条目自身含真代号（大写写法与「代号紧贴汉字」示例）→ 改写为不含真名的等价表述（**纪律：CHANGELOG 条目与 commit message 里同样不得写真实标识**）
- **3.3.3 条目里「闸门区分大小写」的结论已过期** → 改写为「闸门此前区分大小写，该缺口已在 3.3.4 修复：闸门大小写不敏感」
- **SCHEMA 宪法自相矛盾**：§二 一处既写 check「不含结论」又写「最终验收结论在 check」→ 统一为「check 只放方法，对照结果与判定写 tasks 末尾」
- **知识库素材目录名漂移**：`references/` → `resource/`（五名合并后的新名，qwiki 2.7.3 起），并在 SCHEMA 的知识库树旁加指针「知识库目录结构唯一真相源见 qwiki skill 的 SCHEMA.md」
- **README 手动复制块漏 SCHEMA.md**（宪法）→ 补一行并注明「不可省」；仓库结构块 templates 描述「六模板」→ 实际四模板（spec / design / tasks / check）
- **CHANGELOG 同一版本两条**：删末尾重复的 3.3.1 段
- **模板 H1 旧术语**：design「— 方案」→「— 设计」、spec「— 目标」→「— 规格」；spec 小节「做成什么样（成功标准）」→「要什么（成功标准）」（「做成什么样」在体系里专指宪法）
- 版本 3.3.4 → 3.3.5

## 3.3.4 (2026-10-15)

### Fixed
- **发布闸门 publish-check.py 三个洞同批修**（脱敏反复回潮的根因之一：闸门对真实标识零防护却一直报「干净」）：
  ① 代号正则大小写不敏感（旧版只认小写写法，大写写法整体漏）；
  ② 白名单改为**按匹配项豁免**（旧版 `if any(a in line for a in ALLOW): continue` 是整行豁免——一行里出现
  `<项目A>` 就给同行的真名背书；且原 7 个词对 12 条 pattern 全部零命中 = 纯死豁免）；
  ③ 词边界改用显式字符类（`\b` 在 str 模式下 `\w` 含汉字 ⇒「代号紧贴汉字」这类中文常见写法漏检，
  加不加空格决定报不报）。另补 PRJ0## / 裸数字代号 / MAC 连字符 / 凭据变体（`token=`、`Bearer`、中文「密码」加冒号写法）/
  邮箱 六类形态。
- **`--self-test` 样本按已知缺陷类别扩容**（原 15 条只覆盖「正常裸值」一档，上述六类一条样本都没有）；
  自检与扫描共用同一份判定口径（`line_hits`），不再各写一套造成假绿。
- **`scripts/hooks/pre-push` 在推送路径上先跑 `--self-test`**（规则表被改坏时不得静默通过）；
  CHANGELOG 名单统一为超集（SKILL / SCHEMA / install.sh / templates / references / scripts，9 仓文本自此一致）；
  基点改为 `origin/main → gitee/main → 根提交` 三级回落（旧版无 `origin/main` 时回落到 `HEAD~1`，
  多笔提交一起推会只看最后一笔）。
- **新增本机私用名单 `scripts/publish-deny.local`**（gitignore、不进仓）：人名 / 昵称 / 厂商 SDK 名 /
  内部 skill 名这类**无法正则枚举、也不该写进发布仓**的标识，在本机未跟踪文件里逐行列真名，闸门自动一并扫。

### 说明
- 口径全文见 `scripts/publish-check.py` 文件头（已知边界：长 hash 折行、全角句点 IP 不识别；该文件自身在
  `SKIP_FILES` 内，改它时需人工核对）。9 仓共用同一份闸门（md5 一致）——改一处必须批量同步。
- 版本 3.3.3 → 3.3.4

## 3.3.3 (2026-10-14)

### Fixed（install.sh 两处 + 发布闸门，与 qwiki-skill 同款）

- **`--target hermes,claude`（空格形式）从未生效**：解析只认 `--target=`，空格形式把值吞成空串后落进"非交互 = 装全部"分支——而 README / 用法行 / 脚本头部**三处文档全写的空格形式**。现两种形式都支持，且 `--target` 缺参数时直接报错退出（不再静默装全部）。
- **备份落在 skills 扫描根之内**：旧版备份写成 `<skills>/<name>.bak.<时间戳>`，而 agent 按「含 SKILL.md 的目录」发现技能、不看目录名 ⇒ 备份被当成**第二个同名技能**加载（重名歧义下静默跳过其一）。现备份落 `<tool 根>/skills-backup/`（扫描根之外），README 与脚本尾注同步。
- **挂上 pre-push 闸门（脱敏 + CHANGELOG 同步）**：`scripts/publish-check.py`（扫项目代号 / 内网 IP / MAC / 长 hash / 凭据 / 本机路径，自带 `--self-test`）+ `scripts/hooks/pre-push`；启用一次 `git config core.hooksPath scripts/hooks`。理由与脱敏规则同源：**靠人记必然回潮**，检查要做成"推送时自动拦"而不是"记得手动跑"。CHANGELOG 闸门名单 = SKILL.md / SCHEMA.md / install.sh / templates/ / scripts/ / references/。
- **脱敏：正文里的项目代号 / 样机 IP / 代码树路径换占位符**——闸门首扫 5 处，逐条判定后替换（`<项目A>` / `<样机IP A>` / 代码树 `<项目A>_wifi`）。这些标识已随历史提交公开过，本次只保证往后的版本不再含；**闸门此前区分大小写**：正文里的大写写法（如 `<项目A>`）不在命中范围内——该缺口已在 3.3.4 修复：闸门大小写不敏感。
- 版本 3.3.2 → 3.3.3

## 3.3.2 (2026-09-28)

### Added（回灌本机 Hermes 副本的实践沉淀——此前只在本地，未发布）

- **归档 ≠ 闭环完成**：change 收口加「收口三件套审计」（check.md 全勾 / tasks.md 结果表回填 / 项目级 spec.md 变更记录 + 与 qwiki git log 交叉佐证）
- **驱动 CONFIG A/B 试验方法论**（实测沉淀）：编译前 `#ifdef` 分支审计（空桩函数、分支专有变量）、源码与运行 ko 的 CONFIG 漂移核对、A/B 同日交错（A→B→A→B）与重启粒度实验的版级交错（A→B→A'，含镜像副本切版法）、换文件类实验 P0 可写性勘察（只读 rootfs → 重打包/仓库集成路径）、裁决后 ABA 复核 + 同型号多机辨识信号
- **执行载体二选一**（新窗口执行会话 / 派遣子代理）+ 子代理按里程碑拆分与落盘接力、超时截断 transcript 抢救、结果闭环三查
- **并发会话双写防护**：workbench 工件不在 git 下 → 写前查并发（ps/时间戳）、新建 change 前查重、撞 sibling 警示即停并请用户裁定
- 版本 3.3.1 → 3.3.2

## 3.3.1 (2026-08-28)

### Added

- **install.sh 支持 pi 安装目标**（`~/.pi/agent/skills`）

## 3.3.0 (2026-08-18)

### Changed（审查修复）

- **README 安全警告泛化**：`hermes skills install` → 「部分 agent 的 skills install」（多 agent 措辞统一）
- 版本 3.2.0 → 3.3.0

## 3.2.0 (2026-08-18)

### Added

- **ZCode 安装目标**：install.sh 支持 ZCode（探测 `~/.zcode` → 安装到 `~/.zcode/skills/workbench-workflow`），README 补 `--target zcode` 示例，标题泛化「Agent 项目任务管理技能」（去 Hermes 特指）

## 3.1.0 (2026-08-06)

### Changed（合并 openspec-workflow 执行防护）
- **失败熔断铁律**：同一任务连续失败 3 次立即停下报告（含 3 次尝试明细/失败现象/判断/下一步建议），不允许第 4 次自动重试；熔断后用户介入才恢复，失败计数清零
- **参数错误主动检测**：错误参数（波特率/路径/IP）常致进程持续运行不报错——执行后主动检查（烧录 fuser ttyUSB0 / 编译 ps make），发现错误先 kill 释放资源再重试
- **规范先行/颗粒拆细**：任务先对齐规范再执行，任务颗粒拆细便于定位

### 备注
- 本版本为本地合并（2026-08-05 修改未走发布流程），补记 changelog 追认

## 3.0.0 (2026-08-03)

### Changed（四要素命名体系重构）
- **goal.md → spec.md**：目标改规格——「标准由 spec 定」语义顺滑；SPEC=可更改规格身份统一（change 级 spec + 项目级 spec 两级，引用写全路径区分）
- **scheme.md → design.md**：方案改设计——与 design/ 目录流转对齐（design 要点合并进 design/）；消除 scheme/schema 与宪法 SCHEMA 的拼写混淆
- **templates/ 收敛四模板**：spec/design/tasks/check 与四要素一一对应；删除项目约束模板（项目级 spec 按宪法 §五 直接建）和 reference.md 模板（产出物格式见宪法 §四）
- **§四 重定位「知识沉淀衔接」**：workbench 面向任务段（四要素定义任务内工程流转），实践完成触发知识沉淀（产出物入知识库 references/，目录名后改为 resource/），知识库侧机制由对应体系承担，本 skill 不规定（SKILL 不知道 SKILL 原则）
- 项目级 spec.md 全文档加限定（区分 change 级 spec / 项目级 spec）
- 存量 archive 快照（goal.md/scheme.md）不动，文件名不变原则
- 版本 2.0.0 → 3.0.0

## 2.0.0 (2026-08-03)

### Changed（参考分层 A 模式 + 概念平级对齐）
- **宪法提升根目录**：`references/workbench-spec.md` → 根目录 `SCHEMA.md`（与 SKILL.md 平级）——宪法不可替换，templates/references 是参考层
- **SKILL.md 瘦身**：只留操作流程（触发条件/操作导航/新建/闭环），做成什么样内容归 SCHEMA.md（单一真相源，消除双份定义）
- **反模式移入 `references/troubleshooting.md`**：坑按需查阅（A 模式）
- **qwiki 过时副本清理**：`~/qwiki/personal/workbench-spec.md`（旧版 workbench/ 命名）销毁，真相源唯一在 skill
- install.sh 拷贝清单 +1（SCHEMA.md）
- 版本 1.0.0 → 2.0.0

## 1.0.0 (2026-08-01)

### Added
- 初始发布：workbench 项目任务管理体系（change 四要素生命周期）
- 顶部新增「AI 替你完成」使用哲学头节：用户指挥 AI，AI 替用户执行
- triggers：workbench/change/新建任务/闭环/验收/归档/spec/design吸收/四要素
- templates 六件套：goal.md / scheme.md / tasks.md / check.md / spec.md / reference.md（模板已收敛为四件套，见 3.3.5）
- references/workbench-spec.md 完整规范
- 仓库根目录即 skill 本体布局，install.sh 一键安装
