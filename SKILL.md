---
name: qwork
description: 项目任务管理（workbench）：四要素 spec/design/tasks/check 驱动 change，验收→吸收 design→更新项目级 spec→归档闭环，维护进度。
version: 4.9.0
---

# 项目任务管理（workbench）

> **定位**：任务体系跟代码走（项目仓 `0_workbench/`），知识产出留在知识库（规则由知识库侧管理）。
> **规范**见 `SCHEMA.md`；开工前先读 SCHEMA §一/§二/§三——本文件只写怎么做，不替代规范。
> **本机扩展**：技能目录下若有 `references/local/*.md`，先读（不随上游更新覆盖）。

## 使用方式

用户给意图 → §1 路由 → §0 定位 workbench → 缺的信息在对话层问齐 → 四要素落地 → 回报「改了哪些文件 + 状态（施工中/已闭环）」。

**铁律**：给出意图就按规范执行，不反问「要不要先看 spec」；只有缺 change 名/目标/验收标准时才问。

## §0 定位与开工自检

1. **找项目根**：从当前目录向上找含 `0_workbench/` 的目录；没有则找含 `.git` 的最近祖先；仍没有 → 问用户在哪个项目下做，**不擅自建在 agent 工作区**。
2. **骨架不全先补齐**：`0_workbench/` 缺 `spec.md`/`design/`/`change/`/`archive/` 任一项 → 按 SCHEMA §一 补齐，不假定已有 workbench 完整；完全没有 → 建树并过 SCHEMA §七。项目 spec 从 `AGENTS.md` 与现有文档提炼；空白骨架向用户要 1–3 条硬约束，不编造。项目 spec 缺「变更记录」、`design/` 为空也算骨架不全（close 会失败），先补或问用户。
   - **不是 git 仓**：先问用户是否 `git init`（推荐）；不 init 则跳过「开单即提交」，`[x]` 用 `证据:` 路径/用户确认代替 commit hash，归档用 `qwork-archive`（未跟踪路径自动 `mv`），**不得伪造 hash**。
3. **读规则**：顶层 `AGENTS.md` 若存在必须读（构建/测试约定优先于本 skill）；读项目级 `0_workbench/spec.md` 的持久约束与「约束表」。
4. **查重**：`change/` 与 `archive/` 找同主题；有 → 问「并入原 change 还是另立」，另立写清差异。`AGENTS.md` 缺失只提示，不代写。
5. **开工四查**：① 四文件齐 ② spec 有量化成功标准 ③ check 阈值可追溯 spec ④ tasks 阶段可独立执行。
6. **外部代码/环境不在当前仓**：在 tasks「接手须知」记路径、分支、commit 短 hash、获取方式；外部 commit 不能直接当本仓证据；证据用复制进 `data/` 的日志/输出，或用户确认。

## §1 操作路由

| 用户说法 | 做什么 | 依据 |
|---|---|---|
| 新建 change / 开个任务 | §2 四要素 | `templates/*.md` + SCHEMA §二 |
| 改需求 / 改方案 | 更新四要素，变更记 tasks | SCHEMA §二 |
| 接手 / 继续昨天的 change | §5 | — |
| 验收 / 闭环 / 归档 | §4 | SCHEMA §三 |
| 现在什么进度 / 还剩什么 | `change/*/tasks.md` 未勾项（含收口段）+ `archive/` 最近 + 项目级 spec 变更记录 | §4 tasks 收口段 |
| 沉淀到知识库 | 产出物落知识库产出区，登记按知识库侧规则 | SCHEMA §四 |
| 初始化 workbench | §0 | SCHEMA §一/§七 |

## 四要素定位（为什么能闭环）

四要素不是四个文档，是四个问题的答案；缺一个，执行者就得回来问，编排闭环即断开。

| 要素 | 回答 | 定位 | 交接保证 |
|---|---|---|---|
| spec | **做成什么样** | 合同：定义「对」，唯一标准/阈值来源 | 目标、边界、成功标准可判 |
| design | **怎么做** | 图纸：技术路径与决策理由 | 路径与取舍在案，执行者不重开方案 |
| tasks | **怎么组织** | 路书：阶段/顺序/粒度/归属/进度 | 下一步明确，接手能续 |
| check | **怎么验收** | 量具：方法/判据，阈值引 spec | 执行者能自证，第三方能复核 |

## §2 新建 change

1. **命名**：kebab-case（小写+连字符，2–4 段），建议 `<主题>-<类型>`（如 `rx-prealloc-ab`）；不带日期；先查 `change/`、`archive/` 同主题（§0.4）。用户未给名 → 拟 2–3 个候选让用户选。
2. **顺序 spec → check → design → tasks**（验收驱动：先定标准，再定怎么验、再定怎么改）。tasks 开单时就把完整骨架（含「收口」段）建好；边做边填的是状态/结论，不是省段（缺收口段 dispatch 直接 FAIL）。
3. **数据落 `change/<name>/data/`**：原始日志、脚本输出、实验矩阵（不进四要素、默认不入库）；数字结论回填 tasks。
4. **基线未测**：性能/实验型先立 P0；spec 基线写 `待测（tasks P0）`，目标写相对式（`≥ 基线 ×1.10`），底线可留空/待定；P0 后回填绝对值并注 `见 tasks P0`。**目标与判定规则必须开工前定死，基线数值允许后补。**
5. **测量口径**：工具/参数/环境/采样次数/对照序列写进 spec「测量口径」（实验型必填）；check 只写执行步骤与命令并引用 `spec Sx`，不重复参数、序列或阈值。实验型先读 `references/experiment-playbook.md`；裁决阈值归 spec。用户给不出口径 → AI 给默认口径让用户确认。
6. **开单即提交**：四要素骨架写好后先 commit（`<change>: 开单`），再开工；后续每阶段提交（§3）。只 add 本 change 与本次改动文件，**禁止 `git add -A`**；他人在场的 dirty 先问归属，`data/` 默认 ignore。项目级 spec/design 的约束裁决/收口改动**单独提交**，不混进 change 开单 commit。
7. **小任务（同构轻量，不另立通道）**：仅当单 S/单 C、改动 ≤2 非 workbench 文件、≤0.5 人日、不改阈值/口径、不跨 change 依赖时，可压到 1S/1C/1 段 design/3 个施工任务（「收口」段 3 项另计）；仍用同一目录、模板、close/archive/证据门，压缩的是条目数不是门禁。超限 → 收口前补全，不得归档后补；不提供 `--lite`。
8. **项目约束机器核对**：项目级 spec 有 `## 约束表`（ID/指标/上限/单位）时，change spec 必须写 `## 项目约束核对` 逐条列 K；`qwork-check` 在 dispatch/close 都校验。冲突只有两条路：**永久改约束**→改项目级表/变更记录，核对写 `满足` 引用新值；**一次性例外**→核对写 `需变更` + `用户确认: [用户] YYYY-MM-DD`。采样次数写「测量口径」，别塞进性能 S 目标；次数类约束的「条件」列必须写计数基准，为空/无基准词直接 error；机器会抓测量口径里的 `N 次` 与上限比较，但不判断基准语义。相对目标/单位不一致只发 INFO，不阻塞 strict。格式见 SCHEMA §五。
9. **项目级 spec 是上位约束**：项目级「持久约束」「已知天花板」优先于 change spec；change spec 不得静默突破。确需变更，先让用户拍板并更新项目级 `0_workbench/spec.md` 的变更记录，change spec 只引用新值。

**改需求**：改 spec 后必须同步 check（判定口径）、tasks（未完成项/验收表/变更记录）、design（方案）——只改一处视为变更未完成。
- tasks 加变更记录：`YYYY-MM-DD | 改了什么 | 原因 | 影响面`；日期/change/摘要三格齐全。
- 只改目标倍数、基线与口径不变 → 旧 P0/P1 结论可复用并注「基于旧目标」；涉及口径/版本/环境 → 受影响任务改回 `[ ]` 并注 `↻ 因变更重开`；`[x]` 不静默保留，结论失效就降级。
- check 判定口径不得写数值比较/倍数（≤/≥/</>/×），只写「按 spec Sx 判定」；中文「不少于/不超过」不触发正则，但仍应引用 spec。tasks 实测同时对比任务行目标与 spec 目标。目标上调前做可行性核对（design 资源/预算/上限），上限未知先立 P0；超上限先回 design 迭代。

### check.md 怎么写

每个检查项一个 ID（`C1、C2…`），挂到 spec 的某个 `S`；阈值只引 spec，不另立门槛（spec ≥94 就不能在 check 写 ≥90）：

| ID | spec | 检查方法（命令/步骤） | 判定口径 | 类型 |
|----|------|----------------------|----------|------|
| C1 | S1 | `bash scripts/report.sh` | stdout 恰为 `pilot-ok`，exit 0 | 自动 |
| C2 | S2 | 5 次重启循环 | 0 crash | 自动 |

规则：每个 `S` 至少一个 `C`；每个 `C` 必须在 tasks「验收结果」有同名行；**结论留空**（落 tasks）；拒绝「功能正常」。

## §3 施工

- **task 状态**：`[ ]` 未做 / `[x]` 完成（附 commit 短 hash 或证据）/ `[!]` 阻塞（同行写原因与解除条件；未解除不得按通过归档，走 §4 阻塞收口）。`[ ]` 同行写 `BLOCKED_*`/`阻塞原因：`/`等待外部` → `qwork-status` 显示「阻塞（待确认）」并提示改 `[!]`，不自动改。
- **每阶段记 commit 短 hash**（本地 commit，不 push 除非用户要求）；它是回退基线。
- **颗粒拆细**：分析（只读）→ 执行（只改）→ 编译 → 验证，不混在一个任务；单任务目标 ≤3。
- **规范先行**：失败先定位根因（只读）→ 更新 design/tasks（标废弃 + 回退方案）→ 再改代码；不许先改代码后补规范。
- **失败熔断**：同一任务连续失败 3 次 → 停下，报告「3 次尝试 / 每次现象 / 判断 / 下一步选项」，等用户恢复；不许第 4 次自动重试。
- **长任务**：后台跑 + 用产物/标记判完成，不前台 sleep 空等。熔断模板、参数错误检测、长等待纪律见 `references/execution-handoff.md`。

## §4 闭环

1. **自查 tasks 实际状态**（不采信「都打勾了」）：确认有「收口」段且三项都在；`[ ]` 有阻塞说明 → 转 `[!]` 并补解除条件；`[x]` 无证据也算未完成（每个 `[x]` 须有 `→` + 用户确认日期 / 非空证据文件 / 存在的 commit hash 三选一）；`[x]` 同行还写 `BLOCKED_*`/等待/未验证 → 按自相矛盾失败；收口段未勾 = tasks 未完。
2. **逐条跑 check**：每条须是可执行命令 + 期望结果，或明确标人工；散文条目先补；实测回填 tasks「验收结果」，❌ 照实写。`--close` 拒绝含 ❌ 却未走证伪留档的 change。
   - **环境缺失三分**：127/ENOENT/权限/设备不在 = 环境缺失，记 blockers + 解除条件，走 `[!]`/阻塞收口；跑起来但不达标才是 ❌；只有实测证据推翻 spec 才走证伪。
   - 自动检查必须留 `data/` 日志；`qwork-check` 只验记录，不执行命令。`--close --strict` 隐含 `--require-logs`：每个自动项要有 `data/check-<C>.log` 且含独立一行 `exit=0`（`qwork-run` 自动写；手写也算）。
3. **收口三项**：① design 要点合并进 `0_workbench/design/` 现有章节（末尾标 `> 来源: <change>`；新格式缺 design 目录 `--close` 直接失败，legacy 只警告）② **强制**复审项目级 `spec.md` 全文，新增/变更约束、天花板、配置写入并在「变更记录」记一行（无变更也记）③ 产出物落知识库产出区，路径/命名/登记按知识库侧规则；本机无约定先问用户放哪或确认无需（不自创目录）。
4. **归档**（tasks 全勾含收口段之后）：`python3 <skill-dir>/tools/qwork-archive.py <change>`（默认先过 close 门；被跟踪走 `git mv`，把 `.gitignore` 的 `change/` 规则镜像到 `archive/`，复核无 untracked；`--dry-run` 预演，`--commit` 提交）。`--commit` 只提交 `archive/<name>` + 变更过的 `.gitignore`；项目级 spec/design 的收口改动须先单独提交。手工等价：`mkdir -p archive` → `git ls-files` 判断跟踪 → `git mv` → `git status` 复核 `data/**` 是否因路径变化变 untracked 并同步 ignore。
5. **commit**：代码改动单独提交；workbench 文档（含归档移动与 `.gitignore`）用 `qwork-archive --commit` 提交，或与代码一并提交；不 push，提交信息建议 `<change>: 归档收口`。纯文档 change 把证据链写进 tasks 结尾：文件清单 + `git diff --stat <范围>` + 核验输出摘要。

**tasks 收口段（三项全勾才算完结）**：① design 要点吸收（无新增记「无需吸收」）② 项目级 spec 复审 + changelog ③ 产出落库/确认无需；加上全部施工任务 `[x]` 且有证据、每个 `C` 在「验收结果」有行、数据回填，才算 tasks 全勾。`qwork-check --close` 会卡「收口段缺失/仍有 `[ ]`」；tasks 末尾须有「最终：」且与判定一致（无 ❌ 且无 ⚠️ 写通过，有 ❌ 写 `❌ 未通过`，有 ⚠️ 写 `⚠️ 阻塞交付`），缺行或矛盾不得归档。**tasks 全勾 = change 完结，归档只是移动，不另设进度表。**

> 执行会话/子代理回报闭环时，`[x]` 是自报不是证据——先跑**核验三查**（源码 commit / 知识库沉淀 / 归档），三查不过不算闭环；命令见 `references/execution-handoff.md` §五。

> **阻塞收口**：`[ ]`→`[!]`；spec 顶标 `> ⚠️ 阻塞收口：<一句结论>`；tasks 记未验证项 + 解除条件，验收结果 `⚠️ 阻塞交付`，并写 `用户确认: 用户 YYYY-MM-DD`；经确认可归档，但不得写成通过。
>
> **证伪/废弃**：spec 顶标 `> ⚠️ 证伪，状态: 拒绝`，design 加 §证伪记录；tasks 验收 `❌ 未通过（证伪）` + `最终：❌ 未通过`，close 门才放行归档。先干后补标 `> retroactive: YYYY-MM-DD 已施工，归档时补写`。

## §5 接手断点 change

1. **定位断点**：先 `python3 <skill-dir>/tools/qwork-status.py .` 看全项目进度，再 `git status --short` 看工作区残留；`ls -lat 0_workbench/change/<name>/` 与 `data/` 最近 mtime；知识库若为 git 仓再比最近提交；查后台进程是否还在跑（烧录/测试被切断是常态）。
2. **核对记录值**：文档里的设备原值/基线可能与现场不符——以现场读回和数据文件为准，错记当场改，并在收口卡列「证伪/更正项」。
3. **空着的验收表或「收口」段 = 未收口**：把实测回填进表，把收口三项勾掉（数字只躺在 `data/` 里没人看得到）。
4. **汇报三块**：结论（证据是哪条读数）/ 证伪与错记更正 / 未处理与决定不做的项。

## §6 执行载体与交接

- **对话分离**：规划会话产出四要素；执行会话只读 spec/design/check 与 `data/`，对 tasks 只写执行字段（勾选/阶段结论/实测/判定/证据），不得改结构/判据/spec/design/check；有误即停并回报，由规划会话改。两对话只传工件，不传聊天历史。
- **派发就绪**：先跑 `qwork-check.py <change> --dispatch`，再人工过八问（读什么/第一条命令/完成判据/基线目标口径/环境权限/禁止与拍板/启动停止/交付格式）；答成「在之前的对话里」=没冻结。八问全文见 `references/execution-handoff.md`。
- **载体**：新窗口会话或子代理；子代理不 commit/不归档/不写知识库，主对话核验后提交并回填 hash；一代理一里程碑；并发双写先看 `ls -lat`，撞警示即停。
- **回执**：按 `references/execution-handoff.md` §七（完成/证据/偏差/未决/下一步/工作区终态）；接手须知填全（决策权/启动停止/验收人）。

## §7 参考

> `<skill-dir>` = 本 `SKILL.md` 所在目录（安装后如 `~/.dsh/skills/qwork`）；命令里的 `tools/...` 指该目录下，不是项目根。

- `SCHEMA.md` — 宪法：目录结构 / 四要素边界 / 拒绝态 / 流转 / 知识沉淀 / spec 维护 / design 吸收
- `templates/` — spec / design / tasks / check 四模板
- `references/experiment-playbook.md` — 驱动 A/B、固件换版、长测类 change 前必读（判据设计 + 验证链）
- `references/execution-handoff.md` — 派子代理 / 长任务 / 核验 / 并发的完整做法
- `references/troubleshooting.md` — 反模式速查
- `references/local/*.md` — 本机实践扩展（不随上游更新覆盖）
- `tools/qwork-check.py` — 派发/收口门：`--dispatch` / `--close` / `--strict` / `--json`；`--close --strict` 隐含 `--require-logs`
- `tools/qwork-archive.py` — 归档事务：close 门 → `git mv` → archive ignore 镜像 → 复核；`--dry-run` / `--commit`
- `tools/qwork-status.py` — 进度：四要素 / 任务 / C 覆盖 / 下一步；`--json`；`--strict` 在 WIP 超限时退出 1
- `tools/qwork-run.py` — 跑 check 表自动项，日志落 `change/data/check-<C>.log`；`--dry-run`/`--only`/`--timeout`
- `examples/` — 两份填满的黄金样例（`doc-change` 文档类、`experiment-change` 实验类），照抄结构而不是照抄数字

## 支持文件清单

`SKILL.md`、`SCHEMA.md`、`CHANGELOG.md`、`templates/`、`references/`、`examples/`、`tools/`。源仓库 `install.sh` 按此清单安装；安装副本不含 `install.sh`。
