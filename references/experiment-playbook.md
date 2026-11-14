# 实验型 change 执行手册（驱动 A/B / 固件换版 / 长测）

> 按需加载：SKILL.md §7 指向这里。做驱动编译期开关、固件/镜像互换、长稳实验的 change 时先读本文件。
> 长等待与后台作业纪律见 `execution-handoff.md` §四；反模式速查见 `troubleshooting.md`。

## 一、判据先行：spec 预写结局

### A/B 型：双结局

实验型 change 的 spec 预写「双结局判定」（判据/裁决阈值属 spec 的判定规则，check 只引用不另立）（如 gro-mainpath-ab：合并率 >10% 且成本降 → 合入；≈0 或劣化 → 删除证据包，影响面坐标在 spec 列好）——两种结局都有收尾路径，实验永不白做。裁决时判据可能被实测证伪（机制与假设相反：gro 假设省 busrx，实测收益 = 吞吐 +6.3% 且 busrx 反升 8.5% 合并税）——按实测修订判据必须记录修订理由，不许骑墙。

### 探路型：三档结局

跨大版本工程（如内核 3.10→5.15）不一步到位——首期 change = **可行性探路**（官方 SDK 对照勘察 → 官方基线试编 → 尺寸/分区账 → 裁剪量化 → 驱动移植面矩阵 → 分期路线图），spec 预写**三档结局**（可行 = 出路线图派生阶段 2+ / 部分可行 = 记录取舍如降级中间版 / 不可行 = 证据收口），并写明边界「只探路不烧生产」——5.15 烧录验证归阶段 2+ 另立 change，探路期不动生产树（新工作在 SDK 解压副本/独立目录）。用户对探路型 change 的决策词 = 「批准渐进式完成」→ 阶段 2+ 逐期推进，每期自含验收 + 回退点。

### 同 ko 多 change：串行链

改同一驱动的 A/B change 必须串行（变量隔离）；后 change 的 A 基线 = 前 change 合入后状态（spec 注明「合入后基线更新」路径）；编译任何 B 版前做 CONFIG 对齐表（源码 vs 运行 ko 符号，防混入前 change 之外漂移）+ nm 符号 diff（只含目标变化）。

## 二、驱动 CONFIG A/B 验证链

对驱动编译期开关（CONFIG_X =n→=y）做 A/B 验证的 change，执行会话必须遵守以下验证链（同厂商谱系补丁双分支同步场景通用）：

1. **编译前 #ifdef 分支审计（最易踩）**：同厂商补丁双分支同步往往只验证 =n 主路径 → =y 分支（从不编译）藏未适配代码。rx-prealloc 实测两例：① `mai_usb_submit_rx_urb` 在 prealloc=y 分支是**空桩**（只 printk 无 return）→ workqueue 恢复路径全断 → RX 假死（iperf 挂死不退出、RSSI 崩 -85）；② config 分支误用 `skb` 变量（n 路径有 skb、prealloc 路径无）→ 编译 error。**对策**：翻 CONFIG 前全 #ifdef 分支 grep 审计——查未声明变量 + 查空桩函数（函数体只有 printk 无 return）；编译后第一轮测试失败先查 dmesg 错误洪流定位。

2. **源码 Makefile 与运行 ko CONFIG 漂移**：源码值与运行 ko 实际符号会漂移（FILTER_TCP_ACK 源码=n 运行=y 实证）。编译 B 前逐项核对（运行 ko nm 反推 vs 源码 CONFIG），**除目标变量外零漂移**才编；编后 nm diff 只增目标符号、零消失。

3. **A/B 同日交错是硬要求**：环境时段性劣化真实存在（同日下午 RSSI 相同但 A 版 RX 81.9→64.8M）——交错序列 A→B→A→B 才能区分版本差与环境差；单次 A/B 对比会误判。

**3b. 重启粒度实验（固件/内核镜像互换）降级为版级交错 A→B→A'**（fw-swap-test 2026-09-07 规划→执行验证闭环）：状态切换须重启（固件开机由驱动加载）时无法轮内交错——同日连续 A 矩阵 → 换 B 重启验证 → B 矩阵 → 还原 A' 矩阵；A' 段量化环境漂移，裁决只认**超 A/A' 包络**的变化（|Δ| 阈值 spec 预写：吞吐 ≥5% / CPU ≥10% = 实锤，≤漂移 = 关闭）；每段切换先验证加载成功（dmesg 固件 size/版本 + wpa COMPLETED）再进下一段，任何一步不过即回滚收尾（异常结局也是有效结论）；刷前本地 + 设备侧 *.orig 双备份（只读 fs 时退化为本地 pull + 镜像副本，见 3c）；双机同件（如 fw_adid 已同）不换只换差异件。

- **执行实证**：A→A' 同日漂移实测 TX +35.5% / RX P1 +14.8%（≥ 全部 B-A 差——B TX 看似 +41% vs A 被 A' 证伪为时段低值，教科书案例，三段设计是硬门槛非可选项）。
- **镜像副本切版法**：每版 kernel_system_b.image 存副本到 `change/data/`，切版 = cp 副本覆盖 out 镜像 + mai_auto_flash 烧现成镜像（~2 分钟/段，免每段重打包 5-10 分钟）——注意 pack_all 会覆盖 out 镜像，重打包前先备份现版副本；每段烧录后设备 DHCP 换 eth0 IP（实测 5 次全变），串口 serial_login_ip.py 现查勿假设。

**3c. 换文件类实验（固件/配置互换）P0 先验可写性——push 方案可能整体被证伪**（fw-swap-test 2026-09-07 执行实证）：spec 设计的「adb push 覆盖固件 + 设备侧 *.orig」在 `<项目A>` 实测**双败**——/lib/firmware 在 rootfs squashfs **只读**（固件编译期打进 rootfs.img，不是运行时可写文件），设备侧 *.orig cp 报 Read-only file system。P0 勘察必须查 `mount`（ro: /、/system、/ai；rw 仅 /data jffs2 ~1MB、/tmp /mnt tmpfs）再冻结方案，勿凭「设备 Linux 文件可 push 覆盖」的通用假设设计。

- **只读 rootfs 上的换文件替代路径** = 宿主重打包镜像（unsquashfs 解包 rootfs.img → 替换 → mksquashfs，uid/gid/权限/压缩保持原样）→ mai_auto_flash 烧对应分区；若被换件在 rootfs 而驱动 ko 在 /system（独立 squashfs）→ 只烧 rootfs 即零驱动改动，回滚 = 备份原 rootfs.img 烧回。文件级 *.orig 备份仅在目标 fs 可写时成立，只读分区退化为「本地 pull + 保留原镜像」双保险。
- **实际闭环路径（fw-swap-test 用户拍板，比手工 unsquashfs 更优）= 仓库集成**：被换文件若在仓库有源（`<项目A>` 固件源 = `kernel/linux/.../aic8800/fw/aic8800D80/`，make_rootfs.sh ~2325-2367 打包时按 CONFIG_FOR_IPCAM 拷入 system staging）→ 替换源 4 文件 + docker `make rootfs && make pack_all` + 烧对应分区 → `git checkout` 即回滚（固件更新走仓库 commit 是既有模式，git 可回退天然成立）。本设备固件实际在 **system 分区**（/lib/firmware -> ../system/lib/firmware symlink，驱动 ko 同区）→ 只烧 system_b 即零驱动/rootfs 改动。

**3d. 裁决后复核（ABA rerun）惯例 + 同型号多机辨识坑**（fw-swap-test 2026-09-07 复核实证）：

- **复核惯例**：裁决型实验闭环后**用户可能要求复核**——同口径 A→B→A 再跑一组（同日下午环境漂移可小一个量级：TX 漂移 35.5%→1.5%，判别力更强）；rerun 数据落 `change/data/rerun/` 子目录隔离（与首组同名 fwA/fwB 不冲突），复核结果追加到 analysis 文档「§复核」节 + 知识库对应产出摘要同步。
- **复核价值实例**：首组 TX B vs A' +4.2% 擦边信号，复核组稳定时段仅 +1~3% **不重复** → 定性首组 A 段 TX 68.9 为环境时段低值（非 A 固件特性）——疑似增益信号复核不复现 = 环境伪信号，原裁决巩固而非推翻。
- **同型号多机在线必先辨识实验机**（用户纠正实例）：adb devices 多台同型号样机（hostname 相同 / 固件目录同名）时勿按 IP 顺手连——实验机辨识信号 = **现跑固件 md5 与 spec/仓库基线吻合**（fw-swap 误连 `<样机IP A>`/`<样机IP B>` 两样机跑固件 345984B 旧版，真实验机 `<尾段>`（末段 .92）固件 274a469b = spec 274a469b…；样机 fmacfw 无 _ipc 后缀名亦为线索）；连错设备 P0 全部勘察白做 + 方案可能被错误设备状态误导。
- **wpa 工具细节**：wpa_cli 连非默认 ctrl_interface 需 `-p /tmp/wpa_supplicant`（设备 conf 的 ctrl_interface 指向 /tmp，默认 /var/run 报 No such file）；signal_poll 输出键为大写 `RSSI=`/`FREQUENCY=`（小写 grep 'signal' 抓不到，矩阵脚本 RSSI 记录会静默丢）。

4. **测试脚本适配**：复用解析脚本先查其硬编码路径/host 判定（parse_top.py 硬编码旧目录 + 按文件名含 `<项目A>` 判 host，归档后路径失效需 monkey）；设备采集用后台脚本 + 轮询 ALL_DONE 标记，勿 adb 前台阻塞长任务。

5. **测试通道失联先判别设备侧 vs 环境**：iperf server ping 不通 ≠ server 故障——先重启设备验证（曾因驱动缺陷致 WiFi 链路假死、ping 全丢、重启即恢复）；驱动嫌疑用烧回对照版 A/B 判别。
