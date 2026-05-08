---
type: feedback
created: 2026-05-09
---

# 用户纠正-不要使用wc命令

用户指出PowerShell中没有wc命令，应该使用Get-Content | Measure-Object -Line代替。

**Why:** 用户在命令行操作时发现的问题
**How to apply:** 后续所有统计行数的操作使用PowerShell原生命令
