---
name: qwork
description: 项目任务管理（workbench）：四要素 spec/design/tasks/check 驱动 change，验收→吸收 design→更新项目级 spec→归档闭环，维护进度。
version: 4.8.1
category: knowledge
metadata:
  agent:
    triggers: [qwork, workbench, change, 新建任务, 闭环, 验收, 归档, spec, design吸收, 四要素, 接手, 进度]
    related_skills: [adb-tftp, serial-tftp, qwiki]
---

# 项目任务管理（workbench）

> **定位**：任务体系跟代码走（项目仓 `0_workbench/`），知识产出留在知识库（规则由知识库侧管理）。
> **规范**（做成什么样）见 `SCHEMA.md`；本文件只写怎么做。**开工前先读 SCHEMA §一/§二/§三**——本文件不足以替代它。
> **本机扩展**：技能目录下若存在 `references/local/*.md`，先读（本地实践，不随上游更新覆盖）。

## 使用方式

用户指挥，AI 执行，用户不面对命令行。给出任务意图 → 识别操作（§1）→ 定位 workbench（§0）→ 缺的信息在对话层问齐 → 按四要素落地 → 回报「改了哪些文件 + 状态（施工中/已闭环）」。

**铁律**：给出意图就按规范执行，不反问「要不要先看 spec」；只有缺 change 名/目标/验收标准时才问。

## §0 定位与开工自检

1. **找项目根**：从当前目录向上找含 `0_workbench/` 的目录；没有则找含 `.git` 的最近祖先；仍没有 → 问用户在哪个项目下做，**不擅自建在 agent 工作区**。
2. **骨架不全先补齐**：`0_workbench/` 缺 `spec.md`/`design/`/`change/`/`archive/` 任一项 → 按 SCHEMA §一 补齐（**不假定已有 workbench 是完整的**）；完全没有 → 建树并过一遍 SCHEMA §七。项目级 `spec.md` 的内容从 `AGENTS.md` 与现有文档提炼；两者都没有（空白骨架）→ 向用户要 1–3 条硬约束再写入，不凭空编造。
3. **读项目规则**：顶层 `AGENTS.md` 若存在必须读（其构建/测试约定优先于本 skill）；读项目级 `0_workbench/spec.md` 的持久约束。
4. **查重**：`change/` 与 `archive/` 找同主题；有 → 问用户「并入原 change 还是另立」，另立须写清差异。`AGENTS.md` 缺失只提示，不代写。
5. **开工四查**（缺哪项先补）：① 四文件齐 ② spec 有量化成功标准 ③ check 阈值可追溯 spec ④ tasks 阶段可独立执行。
6. **目标代码/环境不在当前仓**：在 tasks「接手须知」记外部路径、分支、commit 短 hash、获取方式；外部 commit **不能**直接当本仓证据；证据用复制进 `data/` 的日志/输出，或用户确认。

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
| spec | **做成什么样** | 合同：定义「对」，唯一标准来源 | 目标、边界、成功标准可判 |
| design | **怎么做** | 图纸：技术路径与决策理由 | 路径与取舍在案，执行者不重开方案 |
| tasks | **怎么组织** | 路书：阶段/顺序/粒度/归属/进度 | 下一步明确，接手能续 |
| check | **怎么验收** | 量具：方法/判据，阈值引 spec | 执行者能自证，第三方能复核 |

## §2 新建 change

1. **命名**：kebab-case（小写+连字符，2–4 段），建议 `<主题>-<类型>`（如 `rx-prealloc-ab`、`partition-fix`）；不强制动词开头、不带日期；先查 `change/`、`archive/` 同主题（§0.4）。用户未给名 → 拟 2–3 个候选让用户选，不自定后不回显。
2. 建 `0_workbench/change/<name>/`。
3. **顺序 spec → check → design → tasks**（验收驱动：先定标准，再定怎么验、怎么改；tasks 边做边填）。成功标准表用 `S1、S2…` 编号，check 的 `C` 项挂到 `S` 上。
4. **数据落 `change/<name>/data/`**：原始日志、脚本输出、实验矩阵（不进四要素、默认不入库）；数字结论回填 tasks。
5. 分析报告落知识库产出区，不塞 change 目录。
6. **基线未测时**：性能/实验型先立 P0 基线任务；spec 基线列写 `待测（tasks P0）`，目标写相对式（如 `≥ 基线 ×1.10`），底线可留空（`—`/`待定（P0 后回填）`），不得凭空写数。P0 测完把绝对值回填 tasks，spec 基线列改 `见 tasks P0` 并记一条变更说明——**目标与判定规则必须开工前定死，基线数值允许 P0 后回填**。
7. **测量口径**：工具/参数/环境/采样次数写进 spec 或 check（实验型必填）；实验型先读 `references/experiment-playbook.md`，把交错序列写进 check、裁决阈值写进 spec。用户给不出口径 → AI 给默认口径让用户确认后写入。
8. **开单即提交**：四要素骨架写好后先 commit（`<change>: 开单`），再开工；后续每阶段提交（§3）。提交只 add 本 change 与本次改动文件，**禁止 `git add -A`**；他人在场的 dirty 先问归属，`data/` 默认 ignore。

四要素缺一不可；**目标与判定规则必须在开工前写好**（基线回填规则见第 6 条）。边界：标准由 spec 定，方法由 check 给，结果落 tasks（SCHEMA §二）。

**改需求**：改 spec 后必须同步 check（判定口径）、tasks（未完成项/验收表/变更记录）、design（方案）——只改一处视为变更未完成。规则：
- tasks 加一行变更记录：`YYYY-MM-DD | 改了什么 | 原因 | 影响面`。
- 只改目标倍数、基线与口径不变 → P0/P1 结论可复用，注「基于旧目标」；涉及口径/版本/环境 → 受影响任务改回 `[ ]` 并注 `↻ 因变更重开`。
- `[x]` 不静默保留：结论失效就降级，并在变更记录说明。改需求后 check 判定口径、tasks 未完成项/验收表必须同步；check 判定口径不得写数值比较/倍数（≤/≥/</>/×），只写「按 spec Sx 判定」；tasks 的实测会同时对比任务行目标与 spec 目标；变更记录行必须日期/change/摘要三格齐全，不能只有表头或空摘要。
- 目标上调前先做可行性核对（design 的资源/预算/上限）；上限未知先立 P0 测量任务，不得直接判可行；超上限先回 design 迭代。复用旧 P0/P1 结论前先复核证据与环境，口径/版本/环境变则重开。同时核对底线仍低于目标，冲突先问用户。

### check.md 怎么写

每个检查项一个 ID（`C1、C2…`），挂到 spec 的某个 `S` 维度上；阈值只引 spec，不另立门槛（spec ≥94 就不能在 check 写 ≥90）：

| ID | spec | 检查方法（命令/步骤） | 判定口径 | 类型 |
|----|------|----------------------|----------|------|
| C1 | S1 | `bash scripts/report.sh` | stdout 恰为 `pilot-ok`，exit 0 | 自动 |
| C2 | S2 | 5 次重启循环 | 0 crash | 自动 |

规则：每个 `S` 至少一个 `C`；每个 `C` 必须在 tasks「验收结果」里有同名行；**结论留空**（结论落 tasks）；拒绝「功能正常」。

## §3 施工

- **task 状态**：`[ ]` 未做 / `[x]` 完成（附 commit 短 hash 或证据）/ `[!]` 阻塞（同行写原因与解除条件；未解除不得以「通过」归档，走 §4 阻塞收口）。若 `[ ]` 同行已写 `BLOCKED_*` / `阻塞原因：` / `等待外部`，`qwork-status` 会显示「阻塞（待确认）」并提示改 `[!]`；它只提示，不自动改状态。
- **每阶段记 commit 短 hash**（本地 commit，不 push 除非用户要求）；它是回退基线。
- **颗粒拆细**：分析（只读）→ 执行（只改）→ 编译 → 验证，不混在一个任务里；单任务目标 ≤3。
- **规范先行**：失败先定位根因（只读）→ 更新 design/tasks（标废弃 + 回退方案）→ 再改代码；不许先改代码后补规范。
- **失败熔断**：同一任务连续失败 3 次 → 停下，报告「3 次尝试 / 每次现象 / 判断 / 下一步选项」，等用户恢复；不许第 4 次自动重试。
- **长任务**：一律后台跑 + 用产物/标记判完成，不前台 sleep 空等。

> 熔断报告模板、参数错误主动检测（串口/编译进程）见 `references/execution-handoff.md` §一；长等待纪律见 §四。

## §4 闭环

1. **先自查 tasks 实际状态**（不采信「都打勾了」）：确认有「收口」段且三项都在；`[ ]` 但同行有阻塞说明 → 转 `[!]` 并补解除条件；`[x]` 无证据也算未完成（`--close` 要求每个 `[x]` 有 `→` + 用户确认日期 / 非空证据文件 / 存在的 commit hash 三选一）；`[x]` 同行还写 `BLOCKED_*`/等待/未验证，按“自相矛盾”直接失败；收口段未勾 = tasks 未完。再对照 check **逐条跑**（每条须是可执行命令 + 期望结果，或明确标注人工判定；散文条目先补）；实测数字回填 tasks「验收结果」，❌ 照实写（不许只在 check 里写结论）。`--close` 会拒绝含 ❌ 却未走证伪留档的 change。
> **环境缺失三分**：命令跑不动（127/ENOENT/权限/设备不在）是**环境缺失**，不是实测不满足，也不是证伪；记 blockers + 解除条件，走 `[!]`/阻塞收口。跑起来但不达标才是 ❌；只有实测证据推翻 spec 才走证伪。自动检查必须留下 `data/` 日志；`qwork-check` 只验记录，不执行命令。
2. design 要点**合并**进 `0_workbench/design/` 现有章节（末尾标 `> 来源: <change>`），不堆文件（对应 tasks 收口段第 1 项）；新格式 change 的项目级 `0_workbench/design/` 缺失，`--close` 直接失败（legacy 只警告）。
3. **强制**复审项目级 `spec.md` 全文：新增约束/天花板/配置 → 更新并在「变更记录」记一行（不是「按需」；对应收口段第 2 项）。
4. 产出物落知识库产出区；路径、命名与登记按知识库侧规则（本 skill 不定义）。**本机无知识库约定时先问用户产出放哪（或确认无需沉淀），不自创目录**（「无约定」= 本机没有可发现的知识库管理技能或目录规则；有则按其规则执行；对应收口段第 3 项）。
5. **归档**（tasks 全勾含收口段之后）：`python3 <skill-dir>/tools/qwork-archive.py <change>`（默认先过 close 门；被跟踪走 `git mv`，并自动把 `.gitignore` 的 `change/` 规则镜像到 `archive/`，复核无 untracked；`--dry-run` 预演，`--commit` 提交）。`--commit` 只提交 `archive/<name>` + 变更过的 `.gitignore`；项目级 spec/design 的收口改动须先单独提交，否则归档 commit 不包含它们。手工等价：`mkdir -p archive` → `git ls-files` 判断跟踪 → `git mv` → `git status` 复核 `data/**` 是否因路径变化变 untracked 并同步 ignore。
6. **commit**：代码改动单独提交；workbench 文档（含归档移动与 `.gitignore`）用 `qwork-archive --commit` 提交，或与代码一并提交；不 push，提交信息建议 `<change>: 归档收口`。纯文档 change 把证据链写进 tasks 结尾：文件清单 + `git diff --stat <范围>` + 核验输出摘要（如 `report.sh → pilot-ok，9B`）。

**tasks 收口段（三项全勾才算完结）**：① design 要点吸收 ② 项目级 spec 复审 + changelog ③ 产出落库/确认无需；加上全部施工任务 `[x]` 且有证据、每个 `C` 在「验收结果」有行、数据回填，才算 tasks 全勾。`qwork-check --close` 会卡「收口段缺失/仍有 `[ ]`」；tasks 末尾须有「最终：」且与判定一致（无 ❌ 且无 ⚠️ 写通过，有 ❌ 写 `❌ 未通过`，有 ⚠️ 写 `⚠️ 阻塞交付`），缺行或矛盾也不得归档。**tasks 全勾 = change 完结，归档只是移动，不另设进度表。**

> 执行会话/子代理回报闭环时，`[x]` 是自报不是证据——先跑**核验三查**（源码 commit / 知识库沉淀 / 归档），三查不过不算闭环；命令见 `references/execution-handoff.md` §五。

> **阻塞收口**（阻塞本身是结论，如工具缺失/环境不可用）：原为 `[ ]` 的阻塞任务先改 `[!]`（状态更正，不算篡改）；spec 顶部标 `> ⚠️ 阻塞收口：<一句结论>`；tasks 写「未验证项 + 解除条件」，验收结果记 `⚠️ 阻塞交付`，并写 `用户确认: 用户 YYYY-MM-DD`（close 门要求确认日期）；**经用户确认后可归档，但不得写成通过**。

> 证伪/废弃：四要素照留，spec 顶部标 `> ⚠️ 证伪，状态: 拒绝`，design 加 §证伪记录（SCHEMA §二）；tasks 验收结果写 `❌ 未通过（证伪）` + `最终：❌ 未通过`，close 门才放行归档。先干后补四要素标 `> retroactive: YYYY-MM-DD 已施工，归档时补写`（机检标记）。

## §5 接手断点 change

1. **定位断点**：先 `python3 <skill-dir>/tools/qwork-status.py .` 看全项目进度，再 `git status --short` 看工作区有无未提交的施工残留；`ls -lat 0_workbench/change/<name>/` 与 `data/` 最近 mtime；知识库若为 git 仓再比最近提交；查是否还有后台进程在跑（烧录/测试跑到一半被切断是常态）。
2. **核对记录值**：文档里的设备原值/基线可能与现场不符——**以现场读回和数据文件为准**，错记当场改，并在收口卡列「证伪/更正项」。
3. **空着的验收表或「收口」段 = 未收口**：把实测数字回填进表，把收口三项勾掉（数字只躺在 `data/` 里没人看得到）。
4. **汇报三块**：结论（证据是哪条读数）/ 证伪与错记更正 / 未处理与决定不做的项。

## §6 执行载体与交接

- **对话分离**：规划会话产出四要素；执行会话**只读** spec/design/check 与 `data/`，对 tasks **只写执行字段**——勾选、阶段结论、测试数据、实测值、判定、收口勾选与证据；不得改 tasks 的阶段结构/判据，不得改 spec/design/check，遇阻塞即退出。判据/阈值有误 → 停，回报建议，由规划会话改。两对话只传工件（文件），不传聊天历史。
- **派发就绪自检（派单前必过）**：先跑 `python3 <skill-dir>/tools/qwork-check.py <change> --dispatch`（机器查 ID/覆盖/接手须知），再人工过八问：① 执行者要读哪些文件、各自是否自足？② 第一条任务、第一条命令是什么？③ 每个任务的完成判据是否可观察？④ 每个指标的基线/目标/测量口径在哪？⑤ 环境/设备/权限从哪来？⑥ 什么绝对不能改、卡住时谁拍板（决策权）？⑦ 什么条件启动、什么条件停止/退回规划？⑧ 做完交什么、按什么格式回报？——任一答成「在之前的对话里」或「执行者自己判断」，就是没冻结，先补再派。
- **载体二选一**：新窗口执行会话，或子代理（主对话决策，子代理实测）。子代理按回执格式带回数据与建议（证据给路径/关键读数），**不 commit、不归档、不写知识库**——提交由主对话核验后完成并回填 hash；独立执行会话可按 §3 每阶段自行 commit。方向性决策留主对话。
- **一代理一里程碑**：编译+烧录+长稳整包必超时；按「烧 B + 短矩阵」「B 长稳」「烧 A + 复测」拆，靠落盘 `change/data/` 接力；给现成 IP/通道，禁止探索。
- **并发双写**：写前看目标目录 `ls -lat` 是否秒级新鲜、工具是否报 sibling 修改；撞警示即停，请用户裁定所有权；归档前复核目录归属。DSH 多会话同进程，别用 `ps | grep hermes` 判并发。
- **执行回执**：执行者按 `references/execution-handoff.md` §七 的格式回报（完成 / 证据 / 偏差 / 未决 / 下一步 / 工作区终态），规划会话核验后再收口。tasks 顶部的「接手须知」必须填全（含决策权、启动/停止条件、验收人）。
- 完整做法（对话分离四阶段、DSH 工具映射、核验三查、长等待纪律、回执与冷启动演练）见 `references/execution-handoff.md`。

## §7 参考

> `<skill-dir>` = 本 `SKILL.md` 所在目录（安装后如 `~/.dsh/skills/qwork`）；命令里的 `tools/...` 指该目录下，不是项目根。

- `SCHEMA.md` — 宪法：目录结构 / 四要素边界 / 拒绝态 / 流转 / 知识沉淀 / spec 维护 / design 吸收
- `templates/` — spec / design / tasks / check 四模板
- `references/experiment-playbook.md` — 做驱动 A/B、固件换版、长测类 change 前必读（判据设计 + 验证链）
- `references/execution-handoff.md` — 派子代理 / 长任务 / 核验 / 并发的完整做法
- `references/troubleshooting.md` — 反模式速查
- `references/local/*.md` — 本机实践扩展（不随上游更新覆盖）
- `tools/qwork-check.py` — 派发/收口门：`--dispatch` / `--close` / `--strict` / `--json`
- `tools/qwork-archive.py` — 归档事务：close 门 → `git mv` → archive ignore 镜像 → 复核；`--dry-run` / `--commit`
- `tools/qwork-status.py` — 全项目进度：四要素 / 任务 / C 覆盖 / 下一步；`--json`；`--strict` 在 WIP 超限时退出 1；WIP 上限读 `QWORK_WIP_LIMIT` 或 `0_workbench/qwork.conf` 的 `wip_limit=`（0/缺省=不限）。
- `tools/qwork-run.py` — 可选执行辅助：跑 check 表「自动」项里反引号命令，日志落 `change/data/check-<C>.log`；`--dry-run`/`--only`/`--timeout`；不替代 close 门。需要强制执行证据时，用 `qwork-check.py <change> --close --require-logs`：每个「自动」C 必须有 `data/check-<C>.log` 且含 `exit=0`。
- `examples/` — 两份填满的黄金样例（`doc-change` 文档类、`experiment-change` 实验类），照抄结构而不是照抄数字

## 支持文件清单

`SKILL.md`、`SCHEMA.md`、`CHANGELOG.md`、`templates/`、`references/`、`examples/`、`tools/`。源仓库的 `install.sh` 按此清单安装；安装副本不含 `install.sh`。
