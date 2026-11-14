# qwork-skill

Agent 项目任务管理技能（skill）—— 基于 0_workbench/ 目录的 change 四要素任务体系。

workbench 让嵌入式/软件开发团队的项目任务管理跟代码走：每个 change 用 spec/design/tasks/check 四要素驱动，验收标准开工前就定好，闭环后 design 吸收 + 项目级 spec 维护 + 知识沉淀。仓库根目录即 skill 本体，用一键脚本或手动复制安装。

## 安装

本 skill 支持多 agent 目标：Hermes / Claude Code / Codex / ZCode / DeepSeek Harness(dsh)。安装脚本自动探测本机已安装的 agent，让用户选择安装目标。

> **本机状态（2026-11-14）**：本地源码与安装已是 **v4.8.3**。安装/升级用 `bash install.sh --local --target dsh`（用当前 checkout，不克隆远端），并以 `bash install.sh --check` 校验一致；远端安装命令仅在已推送后使用。


```bash
# 方式 1：交互选择安装目标（推荐，先下载再执行以保留交互）
curl -fsSL https://gitee.com/GreatBigM/qwork-skill/raw/main/install.sh -o /tmp/install.sh && bash /tmp/install.sh

# 方式 2：指定目标（非交互，含 ZCode）
curl -fsSL https://gitee.com/GreatBigM/qwork-skill/raw/main/install.sh | bash -s -- --target hermes,claude,zcode

# 方式 3：安装到全部检测到的 agent
curl -fsSL https://gitee.com/GreatBigM/qwork-skill/raw/main/install.sh | bash -s -- --all
```

> 脚本等价于手动复制（clone + cp），不经过安全扫描，可先审阅脚本内容再执行。
> 已安装时自动备份旧版本到 `<tool 根>/skills-backup/<skill>.bak.<时间戳>`（**扫描根之外**——备份留在 skills/ 内会被当成第二个同名技能加载），重跑即升级（含版本对比提示）。
> 本机扩展放 `references/local/`：升级时保留，不随上游覆盖（见下节）。
> 开发/验证：`bash install.sh --local --target dsh`（用当前 checkout，不克隆远端）；`bash install.sh --check` 对比安装副本与清单，非 0 退出码 = 有漂移。
> 推送前有闸门（`scripts/publish-check.py` 脱敏 + CHANGELOG 同步）：`git config core.hooksPath scripts/hooks` 启用一次即可。

## 安装（备选：手动复制）

> ⚠️ 注意：部分 agent 的 `skills install`（tap/URL 方式）对 qwork 会触发安全扫描拦截——
> 扫描器将「引用 AGENTS.md」等判定为 dangerous（误报，workbench 本质是管理 AGENTS.md 的任务体系），
> 且 community 来源 + dangerous 判定不可用 --force 绕过。**请使用一键脚本或手动复制安装，不经过扫描。**

```bash
# 1. 克隆本仓库
git clone https://gitee.com/GreatBigM/qwork-skill.git

# 2. 复制到目标工具的 skills 目录（不经过安全扫描）
mkdir -p ~/.hermes/skills/qwork
cp qwork-skill/SKILL.md ~/.hermes/skills/qwork/
cp -r qwork-skill/templates ~/.hermes/skills/qwork/
cp -r qwork-skill/references ~/.hermes/skills/qwork/
cp -r qwork-skill/examples ~/.hermes/skills/qwork/
cp -r qwork-skill/tools ~/.hermes/skills/qwork/
cp qwork-skill/SCHEMA.md ~/.hermes/skills/qwork/   # 宪法，不可省
cp qwork-skill/CHANGELOG.md ~/.hermes/skills/qwork/   # 版本历史（install.sh 同样拷贝）
# ZCode: cp -r 到 ~/.zcode/skills/qwork/（同样别漏 SCHEMA.md 与 CHANGELOG.md）
# dsh:   cp -r 到 ~/.dsh/skills/qwork/（同上）

# 3. 会话内 /reload-skills，或新开会话自动加载
```

## 本机扩展（不污染上游）

个人实践写进技能目录的 `references/local/*.md`：升级时自动保留（`install.sh` 从备份回拷），不随仓库更新覆盖；`SKILL.md` 要求加载时先读这些文件。这样本地差异化不再靠改安装副本——那种改法下次安装就被覆盖。

```bash
mkdir -p ~/.dsh/skills/qwork/references/local
$EDITOR ~/.dsh/skills/qwork/references/local/<主题>.md
```

## 快速上手

> 用户只给意图，以下动作由 AI 按 skill 执行；手动敲仅用于核对。

```bash
# 在项目代码仓创建 0_workbench/ 结构（spec.md / design/ / change/ / archive/）
# 新建 change：
mkdir -p 0_workbench/change/<change_name>/data
# 依次写四要素（确认顺序：spec → check → design → tasks）：
#   spec.md   ← 做成什么样（成功标准量化表：ID/基线/目标 + 约束）
#   check.md  ← 怎么验收（C 项表：ID/spec/方法/判定；阈值引 spec）
#   design.md ← 怎么做（事实约束 → 现状/目标路径 → 决策 → 观测点）
#   tasks.md  ← 执行唯一台账（阶段/顺序/判据 + commit、阶段结论、测试数据、验收结果、收口段）
# 原始日志放 change/<name>/data/，数字结论回填 tasks
# 闭环：验收 → tasks 收口段三项（design 吸收 / 项目 spec 复审 / 产出沉淀）→ 移 archive/
```

## 核心概念

**change 四要素**（同一 change 目录，文件名不变，随归档迁移）：

| 文件 | 内容 | 一句话 |
|------|------|--------|
| spec.md | 规格 | 做成什么样（成功标准量化表 + 约束） |
| design.md | 设计 | 怎么做（技术路径 + 决策依据） |
| tasks.md | 执行台账 | 怎么组织（阶段/顺序/判据）+ 阶段结论、commit、测试数据、验收结果、收口段 |
| check.md | 验收 | 怎么验收（命令 + 判定口径，阈值引 spec） |

> 原始产物（日志/脚本输出/实验矩阵）放同目录 `data/`；数字结论回填 tasks，不另立第二份口径。

> 四要素的闭环：**spec = 做成什么样；design = 怎么做；tasks = 怎么组织；check = 怎么验收**。缺一个，执行者就得回问。
>
> **tasks 是执行唯一台账**：进度、阶段结论、commit、实测、验收结果、收口动作都在这里；tasks 全勾（含收口段）= change 完结，归档只是移动。

**铁律**：
- 标准由 spec 定，方法由 check 给，结果落 tasks——同一信息不两处复述
- check 必须可测试、定量（反例「功能正常」；正例「iperf3 TCP RX ≥ <spec 标准值>」）——阈值一律引自 spec 成功标准表，check 只给方法，不另立标准
- spec.md 永远是单文件 + 自带 changelog，不依赖 git log
- design 吸收 = 合并进现有文档，不堆叠文件
- 归档必检：tasks 全勾（含收口段三项）且无未解除 `[!]`、每个 C 有结果行、数据回填；tasks 全勾即完结，之后才迁 archive
- 派发必检：按 SKILL §6「派发就绪八问」逐条有答案；任一答成「在之前的对话里」就不许派

## 工具（随安装下发）

```bash
# 派发前：四文件、S/C 覆盖、接手须知十字段（负责人可选建议填）
python3 tools/qwork-check.py 0_workbench/change/<name> --dispatch

# 收口前：任务清零、C 结果行、阻塞收口、项目 spec changelog
python3 tools/qwork-check.py 0_workbench/change/<name> --close

# 归档：close 门 → git mv → 补 archive ignore →（可选）提交
python3 tools/qwork-archive.py 0_workbench/change/<name>          # 预演加 --dry-run
python3 tools/qwork-archive.py 0_workbench/change/<name> --commit

# 全项目进度（change/ + archive/）
python3 tools/qwork-status.py .            # 或任意子目录；--json；--strict 检查 WIP 超限
python3 tools/qwork-run.py 0_workbench/change/<name> --dry-run   # 可选：执行自动项并落 data/check-C*.log
python3 tools/qwork-check.py 0_workbench/change/<name> --close --require-logs   # 可选：强制自动项日志
```

> `tools/` 在仓库根或安装后的 skill 目录（如 `~/.dsh/skills/qwork/tools/`），不是用户项目根；装好后把命令里的 `tools/` 换成 `<skill-dir>/tools/`。
>
> WIP 上限可选：在 `0_workbench/qwork.conf` 写 `wip_limit=3`，或设 `QWORK_WIP_LIMIT=3`；`qwork-status` 显示 `WIP：N/3`，超限时 `--strict` 退出 1。
>
> `qwork-check --close` 现在机检：每个 `[x]` 的 `→` 证据（用户确认日期 / 存在的路径 / 存在的 commit）、❌ 必须走证伪留档、⚠️ 必须有确认日期的阻塞收口、项目级 spec 的「变更记录」表行；`qwork-status` 的终态直接调用 close 门，不再自报「可归档」。`qwork-status` 还会把 `[ ]` 同行带 `BLOCKED_*` / `阻塞原因：` / `等待外部` 的任务标成「阻塞（待确认）」，提醒改 `[!]`。
>
> 旧格式：spec 顶部标 `> retroactive` 的存量按 WARNING 降级；未标的按新格式报错（先标标记再补结构，不靠删表头绕过）。
>
> `qwork-archive --commit` 只提交 `archive/<name>` + 变更过的 `.gitignore`；项目级 spec/design 的收口改动先单独提交。commit 失败会回滚移动与 `.gitignore`，不留半归档状态。

## 仓库结构

```
qwork-skill/
├── README.md                        ← 本文件
├── install.sh                       ← 一键安装（--local / --check / --target / --all）
├── SKILL.md                         ← 操作手册（定位/路由/四要素/闭环，仓库根即 skill）
├── SCHEMA.md                        ← 宪法（做成什么样：目录/四要素边界/拒绝态/流转/知识沉淀）
├── CHANGELOG.md                     ← 版本历史（版本号单一真相源在 SKILL.md frontmatter）
├── scripts/                         ← 发布闸门（脱敏 + CHANGELOG 同步，**不随安装下发**）
├── examples/                        ← 填满的黄金样例（doc-change / experiment-change）
├── tests/                           ← 探针回归清单（改版后手跑）
├── tools/qwork-check.py             ← 派发/收口门（随安装下发）
├── tools/qwork-archive.py           ← 归档事务（随安装下发）
├── tools/qwork-status.py            ← 进度总览（随安装下发）
├── templates/                       ← change 四要素四模板（spec / design / tasks / check）
└── references/
    ├── experiment-playbook.md       ← 实验型 change：驱动 A/B、固件换版、长测（按需加载）
    ├── execution-handoff.md         ← 执行交接：熔断、对话分离、子代理、核验三查、并发
    └── troubleshooting.md           ← 反模式速查（按需加载）
```

## 设计理念

- **任务跟代码走**：0_workbench/ 在项目代码仓内，AGENTS.md 顶层独立——workbench 是附加层，不绑定 AI 入口
- **验收驱动**：先定 spec 标准 → 再定 check 方法 → 最后设计 design、拆 tasks
- **拒绝态明确**：证伪的 change 照留四要素 + 标注拒绝，归档不分成败
- **知识沉淀**：分析/实验产出写入知识库产出区；目录、命名与登记规则归知识库侧，本 skill 只做交接

## License

MIT
