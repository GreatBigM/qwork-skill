# workbench 反模式（troubleshooting）

> 排障参考：按需查阅，非必读。主流程见 `SKILL.md`，规范见 `SCHEMA.md`。

## 反模式表

| ❌ | ✅ |
|----|-----|
| 验收写「功能正常」 | 验收写可测试的定量标准 + 判定命令 |
| change 闭环不更新项目级 spec | 强制复审全文，按需更新并记 changelog |
| spec 做成文件夹塞子文档 | spec 永远是单文件 |
| 分析报告放 change 目录 | 放知识库产出区（位置与命名按知识库侧规则） |
| change 只有设计没有验收 | spec/design/tasks/check 四要素缺一不可 |
| archive 分 completed/abandoned 子目录 | 扁平，成败看 spec 顶部状态与 tasks 判定 |
| design 吸收 = 把 design.md 拷过去 | 合并进现有文档对应章节，标来源 change |
| 产出物按 change 建子目录 | 平铺，命名按知识库侧约定 |
| 把知识库的目录/命名/登记规则抄进本 skill | 只写交接与边界，规则归知识库侧 |
| spec.md 改完不记 changelog | 每次改动追加一行 |
| 模板复制后保留示例 `[x]` / ✅❌ 结论 | 模板不预填勾选与结论，示例行建完就删 |
| 验收结论只写在 check.md | check 只放方法；实测与判定落 tasks |
| 把 `<项目A>`/`<host>` 占位符当命令执行 | 先替换真实项目名/路径再跑 |
| tasks 全勾但「测试数据」「验收结果」空着 | 数字回填表内，否则不算收口 |
| tasks 全勾但无「收口」段 | 补 design 吸收 / 项目 spec 复审 / 产出沉淀三项；tasks 全勾含收口段才算完结 |
| 用 `ps \| grep hermes` 判并发（DSH 下） | 看目录 mtime + 工具 sibling 警示 |
| 基线没测就写死绝对目标 | spec 基线写 `待测（tasks P0）`、目标用相对式，P0 后回填 |
| 把 check.md 当验收勾选表 | 勾选在 tasks；check 只放方法与判定 |
| 0_workbench 被 git 跟踪却裸 `mv` 归档 | `git mv`，并同步 `.gitignore`（覆盖 change/ 与 archive/） |
| workbench 缺 design/archive 也照常开工 | 先补齐骨架（SKILL §0） |
| 阻塞任务标 `[x]` 蒙混 | `[!]` + 阻塞收口，经用户确认，不得写成通过 |
| 没有知识库约定就自创目录 | 先问用户产出放哪（或确认无需沉淀） |
| 改了 spec 阈值不同步 check/tasks/design | 变更走 spec → check → tasks/design 同步链，并记原因 |
| 开工不提交四要素骨架 | 开单即 commit（`<change>: 开单`），后续每阶段提交 |
| 改需求后把失效的 `[x]` 静默留着 | 受影响任务改回 `[ ]` 注 `↻ 因变更重开`，并记变更记录 |
| 阻塞任务 `[ ]` 直接归档 | 先改 `[!]`，走阻塞收口（用户确认，不得写成通过） |
| `[x]` 只有勾没有证据 | `→` 后接用户确认日期 / 存在的路径 / 存在的 commit，close 门会逐条查 |
| 全 ❌ 仍 close 通过 | 证伪留档：spec 顶部标证伪、design 记证伪记录、tasks 记最终未通过 |
| check 写散文当验收 | 每条命令 + 期望，或明确标注人工判定 |
| `git mv` 前没建 `archive/` | 先 `mkdir -p 0_workbench/archive` |
| 把实验 |Δ| 阈值写进 check | 阈值属 spec 判定规则，check 只引用 |

## 根因备注

- **归档漏项目级 spec 复审**：tasks 全勾 + 收口三项（design 合并 / 项目级 spec 复审更新 / 产出落知识库）+ 每个 C 有结果行，才算完成——漏 spec 复审即归档未完成。
- **check 越界定标准**：标准由 spec 定、方法由 check 给、结果落 tasks——check 不得出现 spec 之外的门槛（如 spec ≥94 则 check 不得写 ≥90）。
- **基线双头**：基线数字以 tasks「测试数据」为单一权威源，spec 标准表/check 验收的基线列引用此处。
- **假收口**：tasks 标 ✅ + 目录已进 archive/ 仍可能缺 check 结果行、数据回填、tasks 收口段——查「是否真收口」先跑 `qwork-check --close`，再核对收口段三项。
- **边界混淆**：workbench 只负责产出物交接（写清来源 change/日期/结论），知识库的目录、命名、登记与组织模型不属本 skill——抄进来就会两套口径漂移。
