---
name: qwork
description: 项目任务管理体系：change 四要素生命周期、闭环验收、spec 维护，任务全程可控。
version: 3.4.4
category: knowledge
metadata:
  agent:
    triggers: [qwork, workbench, change, 新建任务, 闭环, 验收, 归档, spec, design吸收, 四要素]
---

# 项目任务管理（workbench）

> 合并自 openspec-workflow（2026-08-05）：执行防护（对话分离 + 失败熔断）+ 规范先行/颗粒拆细。

> 宪法（做成什么样）：`SCHEMA.md`——目录结构/四要素边界/拒绝态/流转规则/知识沉淀衔接/项目级 spec 维护/design 吸收
> 2026-07-24 确立。任务体系跟代码走，知识产出留在知识库。

## ⚡ 使用方式（AI 替你完成）

**本技能的使用方式是：用户指挥 AI，AI 替用户执行。用户不面对命令行。**

```
用户: 新建一个 change 做 WiFi 驱动优化 / 验收昨天的 change / 项目现在什么状态
AI:  加载本 skill → 识别操作（新建/修改/闭环/查阅）→ 按 SCHEMA.md 定位 0_workbench/ 结构
AI:  对话层向用户询问缺失信息（change 名称/目标/验收标准）
用户: 提供信息
AI:  按四要素模板创建/更新文档 → 回报结果
```

**铁律：用户给出任务意图 → AI 按四要素规范直接执行，不反问"你要不要先看 spec"。**
信息缺失 → AI 对话层引导用户补齐，拿齐就干。

> **AI 交互约定（agent 必读）**：
> - 操作识别：新建 change / 修改 change / 闭环（验收→吸收 design→更新 spec→归档）/ 查阅状态
> - 信息引导：缺 change 名称/目标/验收标准 → 对话层询问，按 `templates/*.md` 四要素填充
> - 交互式设定优先：路径/名称等参数 AI 问清后写入文档，不让用户手动编辑
> - 执行回报：创建/更新的文件 + 状态（施工中/已闭环）

## 触发条件

- 新建/修改 change
- change 闭环（验收 → 吸收 design → 更新 spec → 移至 archive）
- 写 resource/ 产出（知识库素材）
- 查阅项目当前状态（spec.md）
- 创建新项目的 workbench

## 操作导航

| 输入 | 操作 | 依据 |
|------|------|------|
| 新建 change | 四要素模板创建 | `templates/*.md` + SCHEMA.md §二 |
| 修改 change | 更新四要素 | SCHEMA.md §二 |
| 闭环 change | 验收→吸收→更新 spec→归档 | SCHEMA.md §三 |
| 查阅状态 | 读 spec.md | SCHEMA.md §五 |
| 触发知识沉淀（产出物入知识库） | YYYYMMDD 命名 + 两态 | SCHEMA.md §四 |

> 完整规范（做成什么样）见 `SCHEMA.md`：目录结构/四要素边界约定/拒绝态/流转规则/知识沉淀衔接/项目级 spec.md 维护/design 吸收原则。SKILL.md 只承载操作流程。

## change 四要素（速查）

spec（规格：成功标准+约束）· design（设计：怎么改）· tasks（任务）· check（验收）——四文件同目录 `change/<name>/`，模板 `templates/*.md`；边界约定（标准由 spec 定 / 方法由 check 给 / 结果落 tasks）见 `SCHEMA.md` §二。

### check.md 写法

必须可测试、定量，且**阈值一律取自 spec 成功标准表**（check 不另立门槛）。反例：「功能正常」。正例：

```
- iperf3 TCP RX ≥ <spec 标准值>（基线见 spec 成功标准表）
- 5 次循环重启无 crash
- memcpy 占比 ≤ <spec 标准值>
- wpa_state=COMPLETED 重连时间 ≤ <spec 标准值>
```

## 新建 change 流程

1. 在 `0_workbench/change/` 下创建 `<change_name>/` 目录
2. 依次写 spec.md → check.md → design.md，tasks.md 边做边填（从 `templates/` 复制对应模板起步）
3. 过程中产生的分析报告写入知识库 resource/
4. 四要素缺一不可——验收标准必须在开工前就写好

## change 闭环流程

1. 对照 check.md 逐条确认通过
2. 提取 design.md 关键设计决策，合并到 design/ 对应文档
3. 判断 spec.md 中哪些成为持久约束 → 更新项目级 spec.md + changelog
4. 整个 `<change_name>/` 目录移至 archive/
5. git commit（项目仓）

> 归档检查清单：① design 要点已合并进 design/ ② 项目级 spec.md 已复审并按需更新 ③ 产出物已落知识库。三项全绿才算归档完成（SCHEMA.md §三）。

> **归档 ≠ 闭环完成**（2026-09-07 optimized-vs-competitor 实例）：tasks.md 标 ✅ + 目录已进 archive/ 仍可能缺 check.md 勾选同步、tasks.md 结果表回填、项目级 spec.md changelog 行（该 change 分析/qwiki/归档全做了, 这三件文书滞后一整个周末没人发现）。查「还剩什么没做 / 是否真收口」先跑**收口三件套审计**再答：① check.md 的 [ ] 是否全 [x]（含 P2 分析/产出段, 不只 P1）② tasks.md 数据结果表是否回填（数字须落表, 不能只在分析文档里）③ 项目级 spec.md 变更记录是否有该 change 行——缺哪项当场补齐, 与 qwiki git log 交叉佐证沉淀。

## 接手断点 change（从上个会话/别人手里接）

接手一个已开工的 change 时，**先把「文档写的」和「现场对的」对齐再动手**，顺序不能倒：

1. **定位断点**：`ls -lat change/<name>/` + 它的 `data/**` 最近 mtime 与 qwiki `git log` 比——文档比最后一次 qwiki 提交新 ⇒ 那一段还没沉淀；再看有没有在跑的后台进程（烧录/测试跑到一半被会话切断是常态，见 `serial-tftp` 「接手现场」）。
2. **核对历史记录值**：tasks.md/spec.md 里写下的设备原值、基线数字，可能与现场回读不符（写记录时凭假设/串了口径）。**以现场读回和数据文件为准**，错记当场改掉并在收口卡里列为「证伪/更正项」；带着错记往下做验收，等于拿错基线判通过。
3. **空着的验收表 = 未收口**：`tasks.md` 的验收结果表 / `check.md` 的 [ ] 空着就不算完；把实测数字回填到表里（数字只躺在 `data/` 里没人看得到）。
4. **汇报三块齐全**：结论（通过了什么、证据是哪条读数）／**证伪项与错记更正**／**未处理与决定不做的项**。只报成功的汇报会被当成隐瞒，用户明确要求把否结论一并列出。


## 驱动 CONFIG A/B 试验方法论（rx-prealloc-ab 2026-09-05 实测沉淀）

对驱动编译期开关（CONFIG_X =n→=y）做 A/B 验证的 change，执行会话必须遵守以下验证链（同厂商谱系补丁双分支同步场景通用）：

1. **编译前 #ifdef 分支审计（最易踩）**：同厂商补丁双分支同步往往只验证 =n 主路径 → =y 分支（从不编译）藏未适配代码。rx-prealloc 实测两例：① `mai_usb_submit_rx_urb` 在 prealloc=y 分支是**空桩**（只 printk 无 return）→ workqueue 恢复路径全断 → RX 假死（iperf 挂死不退出、RSSI 崩 -85）；② config 分支误用 `skb` 变量（n 路径有 skb、prealloc 路径无）→ 编译 error。**对策**：翻 CONFIG 前全 #ifdef 分支 grep 审计——查未声明变量 + 查空桩函数（函数体只有 printk 无 return）；编译后第一轮测试失败先查 dmesg 错误洪流定位
2. **源码 Makefile 与运行 ko CONFIG 漂移**：源码值与运行 ko 实际符号会漂移（FILTER_TCP_ACK 源码=n 运行=y 实证）。编译 B 前逐项核对（运行 ko nm 反推 vs 源码 CONFIG），**除目标变量外零漂移**才编；编后 nm diff 只增目标符号、零消失
3. **A/B 同日交错是硬要求**：环境时段性劣化真实存在（同日下午 RSSI 相同但 A 版 RX 81.9→64.8M）——交错序列 A→B→A→B 才能区分版本差与环境差；单次 A/B 对比会误判
3b. **重启粒度实验（固件/内核镜像互换）降级为版级交错 A→B→A'**（fw-swap-test 2026-09-07 规划→执行验证闭环）：状态切换须重启（固件开机由驱动加载）时无法轮内交错——同日连续 A 矩阵 → 换 B 重启验证 → B 矩阵 → 还原 A' 矩阵；A' 段量化环境漂移，裁决只认**超 A/A' 包络**的变化（|Δ| 阈值 spec 预写：吞吐 ≥5% / CPU ≥10% = 实锤, ≤漂移 = 关闭）；每段切换先验证加载成功（dmesg 固件 size/版本 + wpa COMPLETED）再进下一段，任何一步不过即回滚收尾（异常结局也是有效结论）；刷前本地 + 设备侧 *.orig 双备份（只读 fs 时退化为本地 pull + 镜像副本，见 3c）；双机同件（如 fw_adid 已同）不换只换差异件。**执行实证**：A→A' 同日漂移实测 TX +35.5% / RX P1 +14.8%（≥ 全部 B-A 差——B TX 看似 +41% vs A 被 A' 证伪为时段低值, 教科书案例, 三段设计是硬门槛非可选项）；**镜像副本切版法**= 每版 kernel_system_b.image 存副本到 change/data/, 切版 = cp 副本覆盖 out 镜像 + mai_auto_flash 烧现成镜像（~2 分钟/段, 免每段重打包 5-10 分钟）——注意 pack_all 会覆盖 out 镜像, 重打包前先备份现版副本；每段烧录后设备 DHCP 换 eth0 IP（实测 5 次全变）, 串口 serial_login_ip.py 现查勿假设
3c. **换文件类实验（固件/配置互换）P0 先验可写性——push 方案可能整体被证伪**（fw-swap-test 2026-09-07 执行实证）：spec 设计的「adb push 覆盖固件 + 设备侧 *.orig」在 `<项目A>` 实测**双败**——/lib/firmware 在 rootfs squashfs **只读**（固件编译期打进 rootfs.img，不是运行时可写文件），设备侧 *.orig cp 报 Read-only file system。P0 勘察必须查 `mount`（ro: /、/system、/ai；rw 仅 /data jffs2 ~1MB、/tmp /mnt tmpfs）再冻结方案，勿凭「设备 Linux 文件可 push 覆盖」的通用假设设计。**只读 rootfs 上的换文件替代路径** = 宿主重打包镜像（unsquashfs 解包 rootfs.img → 替换 → mksquashfs，uid/gid/权限/压缩保持原样）→ mai_auto_flash 烧对应分区；若被换件在 rootfs 而驱动 ko 在 /system（独立 squashfs）→ 只烧 rootfs 即零驱动改动，回滚 = 备份原 rootfs.img 烧回。文件级 *.orig 备份仅在目标 fs 可写时成立，只读分区退化为「本地 pull + 保留原镜像」双保险。**实际闭环路径（fw-swap-test 用户拍板, 比手工 unsquashfs 更优）= 仓库集成**：被换文件若在仓库有源（`<项目A>` 固件源 = kernel/linux/.../aic8800/fw/aic8800D80/, make_rootfs.sh ~2325-2367 打包时按 CONFIG_FOR_IPCAM 拷入 system staging）→ 替换源 4 文件 + docker `make rootfs && make pack_all` + 烧对应分区 → `git checkout` 即回滚（固件更新走仓库 commit 是既有模式, git 可回退天然成立）。本设备固件实际在 **system 分区**（/lib/firmware -> ../system/lib/firmware symlink, 驱动 ko 同区）→ 只烧 system_b 即零驱动/rootfs 改动
3d. **裁决后复核（ABA rerun）惯例 + 同型号多机辨识坑**（fw-swap-test 2026-09-07 复核实证）：① 裁决型实验闭环后**用户可能要求复核**——同口径 A→B→A 再跑一组（同日下午环境漂移可小一个量级: TX 漂移 35.5%→1.5%, 判别力更强）；rerun 数据落 `change/data/rerun/` 子目录隔离（与首组同名 fwA/fwB 不冲突），复核结果追加到 analysis 文档「§复核」节 + qwiki 卡 summary 同步（summary 三处同步纪律同前）。**复核价值实例**：首组 TX B vs A' +4.2% 擦边信号, 复核组稳定时段仅 +1~3% **不重复** → 定性首组 A 段 TX 68.9 为环境时段低值（非 A 固件特性）——疑似增益信号复核不复现 = 环境伪信号, 原裁决巩固而非推翻。② **同型号多机在线必先辨识实验机**（用户纠正实例）：adb devices 多台同型号样机（hostname 相同 / 固件目录同名）时勿按 IP 顺手连——实验机辨识信号 = **现跑固件 md5 与 spec/仓库基线吻合**（fw-swap 误连 <样机IP A>/<样机IP B> 两样机跑固件 345984B 旧版, 真实验机 `…<尾段>`（末段 .92）固件 274a469b = spec 274a469b…；样机 fmacfw 无 _ipc 后缀名亦为线索）；连错设备 P0 全部勘察白做 + 方案可能被错误设备状态误导。③ wpa_cli 连非默认 ctrl_interface 需 `-p /tmp/wpa_supplicant`（设备 conf 的 ctrl_interface 指向 /tmp, 默认 /var/run 报 No such file）；signal_poll 输出键为大写 `RSSI=`/`FREQUENCY=`（小写 grep 'signal' 抓不到, 矩阵脚本 RSSI 记录会静默丢）
4. **测试脚本适配**：复用解析脚本先查其硬编码路径/host 判定（parse_top.py 硬编码旧目录 + 按文件名含 <项目A> 判 host，归档后路径失效需 monkey）；设备采集用后台脚本 + 轮询 ALL_DONE 标记，勿 adb 前台阻塞长任务
5. **测试通道失联先判别设备侧 vs 环境**：iperf server ping 不通 ≠ server 故障——先重启设备验证（曾因驱动缺陷致 WiFi 链路假死、ping 全丢、重启即恢复）；驱动嫌疑用烧回对照版 A/B 判别

## 长测 / 长等待纪律（2026-10-24 实证：多睡 7.5min 才发现已完成）

1. **只留一个权威 job**：同机并发多条 soak（不同 change 各起一遍）会互相打断、抢设备窗口，「进行中」记录过期。一轮长测供多个 change 共用证据，并在各 change 写**证据映射表**，别各烧各测。
2. **末片 sleep 必须对齐已知终点**：`for i in $(seq N); do sleep 1740; done` 这类轮询若片长乘片数越过终点（3×1740 + 尾片 1700 > 2h），会多等一整轮。以 `结束时间 - 当前时间` 算最后一片，或直接轮询完成标记。
3. **判完成靠产物/标记，不靠时长**：`SOAK_DONE` 文件、`Written: OK`、`partition PASSED`、日志末行时间戳到点，任一命中即推进；等待期不新增竞争唤醒源。
4. **长任务一律 background + notify**：前台 sleep 链会被会话超时/中断打断，且中途无法做别的判断。

## 执行防护（对话分离 + 失败熔断）

### 失败熔断（铁律）

**同一任务连续失败 3 次，立即停下，向用户报告。** 不允许第 4 次自动重试。

- 适用范围：编译、烧录、日志采集、编码、分析等操作
- 报告内容：①已尝试的 3 次各是什么（参数/方法/命令）②每次失败的具体现象（错误信息/串口输出/exit code）③判断（参数错误？环境问题？方法不可行？）④下一步建议（需用户决策的选项）
- **为什么必须有熔断**：没有熔断会陷入"失败→换参数→再失败"循环，消耗大量 token 无法收敛。设备半死/串口无输出/网络不通需要人工介入（断电/连线/配网），自动重试无法解决。3 次足够覆盖"参数错误修正"，超出说明问题不在参数层面
- **熔断后恢复**：用户介入处理后告知"可以继续"，从断点继续，失败计数清零
- **参数错误主动检测**：错误参数（波特率/路径/IP）时进程常持续运行不报错（能 write 但 read 乱码/空），不能被动等超时——执行后主动检查（烧录类 `fuser /dev/ttyUSB0` + `ps aux | grep auto-uboot`；编译类 `ps aux | grep make` + 查日志），发现错误先 `kill -9` 释放资源（串口/终端）再重试

### 对话分离模式

将"无限长的模糊上下文"转化为"有限、确定的执行单元"。核心原理：**两个对话之间只传文件（工件），不传历史（聊天记录）。**

```
规划会话              解耦期              执行会话（新对话）      反馈期（规划会话）
┌──────────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────────┐
│ 分析 + 设计   │ → │ 产出物化  │ → │ 只读 tasks    │ → │ 读阻塞原因    │
│ 冻结工件      │    │ design   │    │ 逐条勾选执行   │    │ 标注原因      │
│ >3模块拆      │    │ tasks    │    │ 遇阻塞→退出   │    │ 修正设计      │
│ 提示退出      │    │ constr.  │    │ 严禁改设计文档  │    │ 产出 v2       │
└──────────────┘    └──────────┘    └──────────────┘    └──────────────┘
```

- 规划会话：讨论定稿，产出 spec/design/tasks/check 工件（本 skill 四要素）
- 解耦期：工件是唯一跨对话载体
- 执行会话：新对话只读 tasks 逐条执行，遇阻塞立即退出（不自行改设计），严禁执行中改设计文档
- 反馈期：阻塞原因带回规划会话，修正设计产出 v2，再开新对话

**执行载体二选一（2026-09-05 起实践，用户明确偏好）**：新开窗口执行会话，或**派遣子代理执行**（主 agent 控制主对话流程与决策，子代理执行带回结果）。子代理模式分工铁律：
- 子代理只做实测+分析，**带回数据与建议（≤500 字摘要），不 commit 源码、不归档、不写 qwiki**——方向性决策（合入/删除/归档收尾/判据修订）留在主对话；工作区终态二选一明确报告（改动留工作区未 commit / 恢复基线干净）
- 设备重活**按里程碑拆子代理**：delegate 子代理有硬性时长/调用上限（实测 ~900s / ~50 calls），编译+烧录切换+短矩阵+600s 长稳+A 同窗复测整包必超限（gro-mainpath-ab 连续 3 个子代理截断教训）。一代理一里程碑（如「烧 B + B 短轮矩阵」/「B 300s×2 长稳」/「烧 A + 同窗复测」），靠落盘 change/data/ 接力断点；长等待用 execute_code sleep 循环保 adb 会话（裸 `&` 后台会在会话断开被杀）
- **子代理超时/截断 ≠ 白跑**（kernel-515 P2 裁剪盘点 2026-09-07 实证）：勘察型 agent 900s 超时无 summary 时，live transcript（~/.hermes/cache/delegation/live/<deleg_id>/task-0.log）常含**完整定量数据**（裁剪省字节表 8 项全在, 仅收尾汇总未写）——`tail` + `grep -oE` 关键输出模式提取即得, 任务 90% 完成勿重派, 只补缺的收尾段；transcript 尾部连续慢全仓 grep（跨仓 -r 无排除 116-180s/次）是超时主因——给子代理任务限 grep 范围（路径排除/maxdepth）
- 给子代理完整环境与现成通道，禁止探索：设备 IP 动态现查（重启必换，/23 扫 5555 + uptime 辨识）、烧录走 adb-tftp `mai_auto_flash.sh enp2s0` original mode（勿自建 TFTP——宿主 sudo 密码子代理没有）、重启后 /tmp 清空重推工具
- 子代理结果回来仍走「闭环声明核验」三查（见下节）

**A/B 型 change 的双结局设计**：实验型 change 的 spec 预写"双结局判定"（如 gro-mainpath-ab：合并率>10% 且成本降 → 合入；≈0 或劣化 → 删除证据包，影响面坐标在 spec 列好）——两种结局都有收尾路径，实验永不白做。裁决时判据可能被实测证伪（机制与假设相反：gro 假设省 busrx，实测收益=吞吐 +6.3% 且 busrx 反升 8.5% 合并税）——按实测修订判据必须记录修订理由，不许骑墙。

**探路型 change（大版本升级/跨代移植/新 SDK 适配）**（kernel-515-upgrade-feasibility 2026-09-07 模式）：跨大版本工程（如内核 3.10→5.15）不一步到位——首期 change = **可行性探路**（官方 SDK 对照勘察 → 官方基线试编 → 尺寸/分区账 → 裁剪量化 → 驱动移植面矩阵 → 分期路线图），spec 预写**三档结局**（可行=出路线图派生阶段 2+ / 部分可行=记录取舍如降级中间版 / 不可行=证据收口），并写明边界「只探路不烧生产」——5.15 烧录验证归阶段 2+ 另立 change，探路期不动生产树（新工作在 SDK 解压副本/独立目录）。用户对探路型 change 的决策词 = 「批准渐进式完成」→ 阶段 2+ 逐期推进每期自含验收+回退点。

**同 ko 多 change 串行链**：改同一驱动的 A/B change 必须串行（变量隔离）；后 change 的 A 基线 = 前 change 合入后状态（spec 注明"合入后基线更新"路径）；编译任何 B 版前做 CONFIG 对齐表（源码 vs 运行 ko 符号，防混入前 change 之外漂移）+ nm 符号 diff（只含目标变化）。

### 规范先行 + 颗粒拆细

- **规范先行**：崩溃/失败发生时，先分析根因（只读）→ 更新设计文档（标记废弃 + 回退方案）→ 按更新后 tasks 执行修复。不能先改代码后补规范——中途被打断则规范误导后续工作
- **颗粒拆细**：分析（只读）→ 执行（只改）→ 编译 → 验证，不混在一个任务里。单任务目标 ≤ 3

### 执行会话闭环声明核验（反馈期必做——[x] 是自报不是证据）

执行会话（独立窗口/子代理）回报「闭环/归档完成」时，tasks/check 的 [x] **不可直接采信**。实测实例（2026-09-05 filter-tcp-ack-ab）：执行会话把「qwiki 沉淀 commit + change 归档」勾成 [x]，实际三项全虚标——qwiki git log 无该 commit、change 目录未移 archive/、驱动源码改动（filter y→n + vmalloc include）也未 commit。规划会话接手补齐后才算真闭环。

接收闭环回报后**核验三查**（各 1 条命令，缺哪项补哪项并回填漏勾的 tasks [ ]）：
1. **源码 commit**：驱动仓 `git log --oneline -5` 最近提交含该 change（本地 commit 绝不 push；A/B 合入 change 最容易漏这一步——测试跑完源码没提交）
2. **qwiki 沉淀**：`cd ~/qwiki && git log --oneline -3` + `ls projects/<项目A>_wifi/` 有 `YYYYMMDD-<change>.md` + INDEX 有行
3. **归档**：`change/<name>` 已不存在 + `archive/<name>` 存在 + 项目级 spec.md 变更记录有该 change 行

### 并发会话双写防护（workbench 工件非 git，双写不可恢复）

0_workbench 通常**不在任何 git 仓下**（如代码树 `<项目A>_wifi` 顶层无 .git，只有 .repo 元数据）→ change 四要素文档被并发会话覆盖后**无 diff 可恢复**。用户可能同时开多个 hermes CLI 终端（gateway/dashboard 之外，`ps aux | grep hermes` 可见 pts/0 等第二实例），各自规划/执行 change。

- **写 change 工件前先查并发**：`ps aux | grep -iE "hermes|claude"` 看有无其他前台会话 + `ls -lat 0_workbench/change/<name>/` 看目标目录最近改动时间戳（秒级新鲜=可能有他方在写）
- **新建 change 前查重**：`ls 0_workbench/change/ 0_workbench/archive/` 找同主题已存在 change（如已有 filter-tcp-ack-ab 只有 spec、prealloc-txq-deglobalize 与 rx-prealloc 同名易混）——先确认是补全还是新建，避免重复规划
- **写结果出现 sibling 警示即停**：工具返回 "modified by sibling subagent ... but this agent never read it" = 另一会话刚写过同一文件。此时**不要静默覆盖**——停下向用户报告（哪个会话/终端可能在规划同一 change），请用户裁定所有权后以一方为准；继续覆盖会把对方未落盘的规划丢进黑洞
- 归档/闭环同理：移 archive/ 前先复核目录归属，防止把别的会话正在施工的 change 误移

## 相关文档

- `SCHEMA.md` — 宪法（做成什么样：目录结构/四要素边界/拒绝态/流转/产出规范/spec 维护/design 吸收）
- `references/troubleshooting.md` — 反模式（坑，按需查）

## 支持文件清单

本 skill 依赖以下模板与参考文件（安装时随 SKILL.md 一并打包，请勿删除）：

- 模板：`templates/spec.md`、`templates/design.md`、`templates/tasks.md`、`templates/check.md`
- 宪法：`SCHEMA.md`（与 SKILL.md 平级，随安装拷贝）
- 参考：`references/troubleshooting.md`
