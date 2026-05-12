# my-text 项目说明文档

## 项目概述

这是一个基于 Trae IDE 的智能体团队调度系统，包含多智能体协作、记忆系统、工作流引擎、监控告警等核心功能。

## 目录结构

```
my-text/
├── .trae/                          # Trae IDE 配置目录
│   ├── agents/                     # 智能体定义
│   │   ├── code_executor_代码执行_agent.md
│   │   ├── dispatcher_智能体团队调度员_agent.md
│   │   ├── monitor_监控智能体_agent.md
│   │   ├── nuwa_女娲造人_agent.md
│   │   └── ... (23个专业智能体)
│   ├── algorithms/                 # 算法层
│   │   ├── game_theory.py          # 博弈论算法
│   │   ├── vector_matcher.py       # 向量匹配算法
│   │   ├── anomaly_detector.py     # 异常检测
│   │   └── load_balancer.py        # 负载均衡
│   ├── api/                        # API接口
│   │   └── management_api.py
│   ├── cache/                      # 缓存系统
│   │   ├── lru_cache.py
│   │   ├── lfu_cache.py
│   │   └── ttl_cache.py
│   ├── ml/                         # 机器学习模块
│   │   ├── vector_database.py
│   │   ├── recommender.py
│   │   └── rl_scheduler.py
│   ├── monitoring/                 # 监控系统
│   │   ├── agent_monitor.py
│   │   └── metrics_collector.py
│   ├── rate_limiting/              # 限流熔断
│   │   ├── circuit_breaker.py
│   │   ├── token_bucket.py
│   │   └── distributed_lock.py
│   ├── skills/                     # 技能库
│   │   ├── auto-doc/              # 自动文档生成
│   │   ├── auto-memory/           # 自动记忆
│   │   ├── auto-refactor/         # 自动重构
│   │   ├── my-code-review/        # 代码审查
│   │   └── nuwa-skill/            # 女娲造人技能
│   ├── workflows/                  # 工作流引擎
│   │   ├── workflow_engine.py
│   │   └── enhanced_workflow_engine.py
│   ├── memories/                   # 记忆系统
│   │   ├── user/                  # 用户记忆
│   │   ├── project/               # 项目记忆
│   │   └── reference/             # 参考资料
│   └── rules/                      # 规则配置
│       ├── core/                  # 核心规则
│       ├── extension/             # 扩展模块
│       └── workflow/              # 工作流模板
├── SafeYuanbaoHelper.ps1          # 腾讯元宝安全内存管理工具
├── WebView2Monitor.ps1            # WebView2进程监控脚本
├── WebView2Config.reg             # WebView2注册表配置
└── TestWebView2Fix.ps1            # WebView2修复测试脚本
```

## 核心功能模块

### 1. 智能体系统 (23个专业智能体)

| 智能体 | 功能 |
|--------|------|
| dispatcher_agent | 智能体团队调度员 |
| monitor_agent | 监控智能体 |
| code_executor_agent | 代码执行智能体 |
| rule_interpreter_agent | 规则解释智能体 |
| society_of_mind_agent | 心智社会智能体 |
| graphrag_agent | 知识图谱检索 |
| fastapi_agent | FastAPI开发 |
| streamlit_agent | Streamlit开发 |

### 2. 记忆系统（三层记忆）

| 类型 | 存储内容 | 生命周期 |
|------|---------|---------|
| 工作记忆 | 当前对话上下文 | 24小时 |
| 情景记忆 | 任务历史执行记录 | 30天 |
| 语义记忆 | 领域知识术语 | 持久 |

### 3. 工作流引擎

- `parallel_gateway` - 并行网关
- `seq_flow` - 顺序流
- `game_theory` - 博弈模式
- `monitor_flow` - 监控流
- `conditional_branch` - 条件分支

### 4. 技能库

| 技能 | 功能 |
|------|------|
| auto-doc | 自动文档生成 |
| auto-memory | 自动记忆处理 |
| auto-refactor | 自动代码重构 |
| my-code-review | 代码审查 |
| nuwa-skill | 女娲造人技能 |

### 5. 算法层

- **博弈论算法**: 纳什均衡、博达计数
- **调度算法**: 优先级队列、最小负载
- **异常检测**: Z-score、IQR检测
- **缓存算法**: LRU、LFU

### 6. 可观测性系统

- 指标收集（请求计数、延迟直方图）
- 分布式追踪
- 结构化日志

## WebView2 相关工具

### SafeYuanbaoHelper.ps1

腾讯元宝安全内存管理工具 v3.0

**功能列表**:
- [1] System Status Check - 系统状态检查
- [2] Safe Cleanup Mode - 安全清理（保护元宝）
- [3] Safe Monitor Mode - 监控模式
- [4] System Repair - 系统修复（需管理员）
- [5] One-Click Diagnose - 一键诊断
- [6] Edge Cleanup Tool - Edge清理工具

**特点**:
- 安全模式：不终止正在运行的元宝进程
- 用户确认提示：操作完成后等待确认
- 完善的错误处理

### WebView2Monitor.ps1

WebView2 进程监控脚本

**功能**:
- 实时监控系统时间
- 监控 WebView2 进程内存使用
- 自动终止高内存进程
- 可配置检查间隔（默认30分钟）

### WebView2Config.reg

注册表配置文件，优化 WebView2 设置：
- 禁用 GPU 加速
- 设置内存限制
- 禁用后台扩展

## 快速开始

### 运行 SafeYuanbaoHelper

```powershell
.\SafeYuanbaoHelper.ps1
```

### 运行 WebView2 监控

```powershell
.\WebView2Monitor.ps1
```

### 查看 WebView2 版本

```powershell
.\CheckWebView2Version.ps1
```

## 技术栈

- **语言**: Python, PowerShell
- **框架**: FastAPI, Streamlit
- **算法**: 向量匹配、博弈论、异常检测
- **架构**: 多智能体协作、事件驱动

## 版本信息

- **L1版本**: 1.4
- **L2版本**: 2.9
- **L3版本**: 2.9
- **更新日期**: 2026-05-11

## 文档维护

| 文档类型 | 路径 |
|---------|------|
| 核心规则 | `.trae/rules/core/` |
| 扩展模块 | `.trae/rules/extension/` |
| 工作流模板 | `.trae/rules/workflow/` |
| 智能体定义 | `.trae/agents/` |
