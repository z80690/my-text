# TRAE 规则入口文件

@meta-cognition

## 自动加载规则配置

### 核心框架
@import "core/智能体团队调度员_v2.8.md"
@import "core/会话记忆模块.md"
@import "core/持久记忆模块.md"

### 扩展模块
@import "extension/智能体团队调度员_扩展模块_v2.8.md"
@import "extension/工具优先原则_v1.0.md"
@import "extension/蜂群模式与多智能体协作_v1.0.md"
@import "extension/智能体模块化组合系统_v1.0.md"
@import "extension/CloudCode记忆系统实现规则_v1.0.md"

### 工作流模板
@import "workflow/高级工作流模板索引_v3.0.md"

### 智能体定义
@import "agents/代码执行智能体_v3.2.md"
@import "agents/规则解释智能体_v1.0.md"
@import "agents/nuwa_女娲造人_agent.md"
@import "agents/monitor_监控智能体_agent.md"
@import "agents/dispatcher_智能体团队调度员_agent.md"

### 自动记忆系统
@import "extension/AI自动记忆行为规则_v1.0.md"

### 增强功能模块
@import "agent_protocol.py"
@import "config_templates.py"
@import "smart_recommender.py"
@import "api/management_api.py"
@import "memory_system.py"

### 规则索引
@import "INDEX.md"

---

## 加载优先级

| 优先级 | 模块 | 说明 |
|-------|------|------|
| P0 | 核心框架 | 调度员v2.8核心能力、记忆模块 |
| P1 | Cloud Code记忆系统 | Dream整合、智能检索、验证机制、准入过滤 |
| P2 | 扩展模块 | 23智能体详细定义、工具优先原则、蜂群模式 |
| P3 | 工作流模板 | 9种工作流定义 |
| P4 | 智能体定义 | 代码执行、规则解释、女娲、监控、调度 |
| P5 | **AI自动记忆** | AI行为规则 - 每次回复自动记忆 |
| P6 | 增强功能 | agent_protocol、config_templates、smart_recommender、management_api、memory_system |
| P7 | 规则索引 | 快速导航索引 |

---

## 触发条件

以下关键词将自动触发调度模式：
- 调度、派单、v2.8、架构
- 代码执行、规则解释、智能体
- 工作流、博弈、并行执行
- 女娲、蒸馏、造skill
- 配置模板、一键部署
- 智能推荐、场景识别
- **Cloud Code、记忆系统、Dream、智能检索**

---

## Cloud Code记忆系统核心改进

### 四大精髓（余承东指示）

| 精髓 | 说明 |
|------|------|
| **主动整理** | Dream机制：≥24小时且≥5会话自动触发整合、剪枝、更新 |
| **智能检索** | 小模型检索员：对话前注入前3-5条相关记忆 |
| **严谨验证** | 使用前验证："记忆说X存在"不等于"X现在存在" |
| **质量把控** | 准入过滤：只记录无法从代码/Git历史推导的信息 |

### 记忆类型与过期策略

| 类型 | 存储路径 | 过期策略 |
|-----|---------|---------|
| User | `memories/user/` | 90天未访问标记审核 |
| Feedback | `memories/feedback/` | 180天未访问自动归档 |
| Project | `memories/project/` | 365天未访问标记审核 |
| Reference | `memories/reference/` | 无限期，手动清理 |

---

## AI行为约束（强制）

**每次回复必须自动执行**：
1. 分析用户消息是否为暗知识
2. 自动分类到正确记忆类型（User/Feedback/Project/Reference）
3. 应用准入过滤规则（不记录可推导信息）
4. 自动写入记忆文件
5. 静默执行，不告知用户

**记忆写入规则**：
- ❌ 不记录代码模式（用grep获取）
- ❌ 不记录文件结构（用ls获取）
- ❌ 不记录Git历史（用git log获取）
- ❌ 不记录临时任务状态
- ✅ 只记录无法从代码和Git历史推导的信息

---

## 版本信息

- **版本**: v2.9
- **日期**: 2026-05-10
- **状态**: 三层同步完成 + Cloud Code记忆系统集成
- **L1版本**: 1.4
- **L2版本**: 2.9
- **L3版本**: 2.9
- **同步状态**: ✅ L1/L2/L3 完全同步
- **Cloud Code整合**: ✅ 四大精髓已集成
