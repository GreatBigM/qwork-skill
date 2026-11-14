# build-doc-refresh — 任务

## 接手须知（派发前填满）

- 负责人：lead

- 必读：`spec.md` / `design.md` / `check.md` + 项目级 `0_workbench/spec.md`
- 环境/前置：docker 可用；仓库只读权限；镜像 tag 记录在 `data/env.txt`
- 绝对禁止：不改 `scripts/*.sh`；不 push；不动其他文档
- 决策权：用户批 spec 变更；规划会话批归档；阻塞找用户
- 启动条件：拿到仓库与 docker 权限；镜像可拉取
- 停止/重规划条件：同一命令失败 3 次，退回规划会话
- 完成判据：每条任务行末「判据」；验收按 check 逐项
- 卡住时：停在失败命令，附输出与已试参数，按回执格式回报给规划会话
- 交付：tasks 勾选 + `data/` 证据 + 执行回执

## P1 盘点

- [x] 记录 3 条命令现状（判据：各跑一次，退出码与耗时进 `data/baseline.txt`）→ 证据: data/evidence.md
> 阶段结论：3 条命令可复现，基线 25 min，失效链接 2 个。

## P2 改写

- [x] `docs/build.md` 参数对齐（判据：diff 只含参数与输出说明）→ 证据: data/evidence.md
- [x] `docs/quickstart.md` 命令与链接修正（判据：C2 输出 `0 broken`）→ 证据: data/evidence.md
> 阶段结论：两份文档已对齐，链接 0 broken，待干净容器复跑。

## P3 验证

- [x] 干净容器逐条执行（判据：C1/C3/C4 通过）→ 证据: data/evidence.md
- [x] 独立验收（判据：验收人按 check 复跑并签字）→ 证据: data/evidence.md
> 阶段结论：干净容器全过，验收人复跑通过；总耗时 14 min。

## 变更记录

| 日期 | 改了什么 | 原因 | 影响面 |
|------|---------|------|--------|
| 2026-11-14 | 目标耗时 20→15 min | 用户要求 | spec 目标 / check C3 |

## 测试数据

| 指标 | 本次 | 基线 | 目标(spec) |
|------|------|------|-----------|
| 命令成功 | 3/3 | 2/3 | 3/3 |
| 失效链接 | 0 | 2 | 0 |
| 耗时 | 14 min | 25 min | ≤15 |

## 验收结果

| ID | 目标(spec) | 实测 | 判定 |
|----|-----------|------|------|
| C1 | S1: 3/3 | 3/3 | ✅ |
| C2 | S2: 0 | 0 | ✅ |
| C3 | S3: ≤15 min | 14 min | ✅ |
| C4 | S1: 无缓存依赖 | 两次均 0 | ✅ |

最终：通过

## 收口

- [x] design 要点合并进 `0_workbench/design/`（无新增记「无需吸收」）→ 证据: data/evidence.md
- [x] 项目级 `spec.md` 复审并记变更记录（无变更也记一行）→ 证据: data/evidence.md
- [x] 产出物落知识库或确认无需沉淀 → 证据: data/evidence.md

## 证据链

- 文件：`docs/build.md`、`docs/quickstart.md`
- 校验：`git diff --stat`；`check-links.sh` 输出 `0 broken`；计时 14 min
