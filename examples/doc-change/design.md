# build-doc-refresh — 设计

## 事实约束

| 约束 | 说明 |
|------|------|
| 文档位置 | `docs/build.md`、`docs/quickstart.md` |
| 脚本接口 | `scripts/build.sh --strict` |
| 环境 | 干净容器，无缓存 |

## 现状路径

文档调用 `build.sh --old-flag` → 脚本报 unknown option → 新人卡住。

## 目标路径

文档命令与 `scripts/build.sh --help` 对齐；链接改为相对路径。

## 核心设计

- 只改参数与路径，不重排章节：降低 review 成本。
- 不合并三条命令：保留分步可读性。
- 基线「3 条中 1 条失败」是实测，不是估计。

## 资源预算

- 文档改动约 40 行；无新增依赖。

## 风险表

| 风险 | 影响 | 缓解 |
|------|------|------|
| 容器网络差异 | 命令成功但拉取慢 | 记录镜像 tag，超时单列 |

## 观测点

- 无额外观测点；验收指标见 check C1–C4。

## 改动范围（文件级清单）

- `docs/build.md` ← 参数与输出说明
- `docs/quickstart.md` ← 命令与链接
