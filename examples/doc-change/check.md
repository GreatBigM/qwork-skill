# build-doc-refresh — 验收

> 只放方法与判定口径；阈值引 spec；结论落 tasks。

## 验收项

| ID | spec | 检查方法（命令/步骤） | 判定口径 | 类型 |
|----|------|----------------------|----------|------|
| C1 | S1 | `bash scripts/build.sh --strict` | exit 0 | 自动 |
| C2 | S2 | `bash scripts/check-links.sh docs/` | 输出 `0 broken` | 自动 |
| C3 | S3 | 干净容器连跑三次并计时 | 按 spec S3 目标判定（目标值见 spec） | 自动 |
| C4 | S1 | 干净容器重复 C1 两次 | 均 exit 0 | 自动 |

> 验收人：独立验收（另一会话按本文件执行）。
