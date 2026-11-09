# Changelog

本文件记录版本历史。版本号定义在 SKILL.md frontmatter 的 `version` 字段（单一真相源）。

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
