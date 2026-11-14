# build-doc-refresh — 验收

> 每条可执行；阈值引 spec；结论落 tasks。

## 功能

- C1 `bash scripts/build.sh --strict` → exit 0（spec:命令可复现/目标）
- C2 `bash scripts/check-links.sh docs/` → `0 broken`（spec:内部链接/目标）

## 性能

- C3 计时：三次中位数 ≤15 min（spec:跑通耗时/目标）

## 稳定性

- C4 在干净容器重复 C1 两次 → 均 exit 0（无缓存依赖）

> 验收人：独立验收（另一会话按本文件执行）。
