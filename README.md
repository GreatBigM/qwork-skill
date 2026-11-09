# workbench-skill

Agent 项目任务管理技能（skill）—— 基于 0_workbench/ 目录的 change 四要素任务体系。

workbench 让嵌入式/软件开发团队的项目任务管理跟代码走：每个 change 用 spec/design/tasks/check 四要素驱动，验收标准开工前就定好，闭环后 design 吸收 + 项目级 spec 维护 + 知识沉淀。仓库根目录即 skill 本体，用一键脚本或手动复制安装。

## 安装

本 skill 支持多 agent 目标：Hermes / Claude Code / Codex / ZCode。安装脚本自动探测本机已安装的 agent，让用户选择安装目标。

```bash
# 方式 1：交互选择安装目标（推荐，先下载再执行以保留交互）
curl -fsSL https://gitee.com/GreatBigM/workbench-skill/raw/main/install.sh -o /tmp/install.sh && bash /tmp/install.sh

# 方式 2：指定目标（非交互，含 ZCode）
curl -fsSL https://gitee.com/GreatBigM/workbench-skill/raw/main/install.sh | bash -s -- --target hermes,claude,zcode

# 方式 3：安装到全部检测到的 agent
curl -fsSL https://gitee.com/GreatBigM/workbench-skill/raw/main/install.sh | bash -s -- --all
```

> 脚本等价于手动复制（clone + cp），不经过安全扫描，可先审阅脚本内容再执行。
> 已安装时自动备份旧版本到 `<tool 根>/skills-backup/<skill>.bak.<时间戳>`（**扫描根之外**——备份留在 skills/ 内会被当成第二个同名技能加载），重跑即升级（含版本对比提示）。
> 推送前有闸门（`scripts/publish-check.py` 脱敏 + CHANGELOG 同步）：`git config core.hooksPath scripts/hooks` 启用一次即可。

## 安装（备选：手动复制）

> ⚠️ 注意：部分 agent 的 `skills install`（tap/URL 方式）对 qwork 会触发安全扫描拦截——
> 扫描器将「引用 AGENTS.md」等判定为 dangerous（误报，workbench 本质是管理 AGENTS.md 的任务体系），
> 且 community 来源 + dangerous 判定不可用 --force 绕过。**请使用一键脚本或手动复制安装，不经过扫描。**

```bash
# 1. 克隆本仓库
git clone https://gitee.com/GreatBigM/workbench-skill.git

# 2. 复制到目标工具的 skills 目录（不经过安全扫描）
mkdir -p ~/.hermes/skills/qwork
cp workbench-skill/SKILL.md ~/.hermes/skills/qwork/
cp -r workbench-skill/templates ~/.hermes/skills/qwork/
cp -r workbench-skill/references ~/.hermes/skills/qwork/
cp workbench-skill/SCHEMA.md ~/.hermes/skills/qwork/   # 宪法，不可省
cp workbench-skill/CHANGELOG.md ~/.hermes/skills/qwork/   # 版本历史（install.sh 同样拷贝）
# ZCode: cp -r 到 ~/.zcode/skills/qwork/（同样别漏 SCHEMA.md 与 CHANGELOG.md）

# 3. 会话内 /reload-skills，或新开会话自动加载
```

## 快速上手

```bash
# 在项目代码仓创建 0_workbench/ 结构（spec/design/change/archive）
# 新建 change：
mkdir -p 0_workbench/change/<change_name>
# 依次写四要素（确认顺序：spec → check → design → tasks）：
#   spec.md   ← 规格：要什么（成功标准量化表：维度/基线/目标）
#   check.md  ← 验收：怎么算完（可执行命令，定量）
#   design.md ← 设计：怎么改（事实约束 → 现状 → 目标 → 核心设计）
#   tasks.md  ← 任务：做到哪（分阶段打勾，记 commit hash + 测试数据）
# 闭环：check 验收通过 → design 合并进 design/ → 项目级 spec.md 复审更新 → 移 archive/
```

## 核心概念

**change 四要素**（同一 change 目录，文件名不变，随归档迁移）：

| 文件 | 内容 | 一句话 |
|------|------|--------|
| spec.md | 规格 | 要什么（成功标准量化表 + 约束） |
| design.md | 设计 | 怎么改（可评审技术路径） |
| tasks.md | 任务 | 做到哪（每步打勾，记 commit/测试数据/验收结果） |
| check.md | 验收 | 怎么算完（可测试定量标准） |

**铁律**：
- 标准由 spec 定，方法由 check 给，结果落 tasks——同一信息不两处复述
- check 必须可测试、定量（反例「功能正常」；正例「iperf3 TCP RX ≥ <spec 标准值>」）——阈值一律引自 spec 成功标准表，check 只给方法，不另立标准
- spec.md 永远是单文件 + 自带 changelog，不依赖 git log
- design 吸收 = 合并进现有文档，不堆叠文件
- 归档必检：design 合并 + 项目级 spec 复审 + 产出物落知识库，三项全绿才算完

## 仓库结构

```
workbench-skill/
├── README.md                        ← 本文件
├── install.sh                       ← 一键安装脚本
├── SKILL.md                         ← 操作手册（触发条件/操作流程，仓库根即 skill）
├── scripts/                       ← 发布闸门（脱敏 + CHANGELOG 同步，**不随安装下发**）
├── SCHEMA.md                        ← 宪法（做成什么样：四要素边界/拒绝态/流转/产出规范）
├── CHANGELOG.md                     ← 版本历史（版本号单一真相源在 SKILL.md frontmatter）
├── templates/                       ← change 四要素四模板（spec / design / tasks / check）
└── references/
    └── troubleshooting.md           ← 反模式（坑，按需查）
```

## 设计理念

- **任务跟代码走**：0_workbench/ 在项目代码仓内，AGENTS.md 顶层独立——workbench 是附加层，不绑定 AI 入口
- **验收驱动**：先定 spec 标准 → 再定 check 方法 → 最后设计 design、拆 tasks
- **拒绝态明确**：证伪的 change 照留四要素 + 标注拒绝，归档不分成败
- **知识沉淀**：分析/实验产出写入知识库 resource/（YYYYMMDD-标题.md，两态裁决）

## License

MIT
