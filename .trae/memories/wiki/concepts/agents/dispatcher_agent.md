# 智能体团队调度员

## 核心信息
- **创建日期**: 2026-05-23
- **最后更新**: 2026-05-23
- **来源**: .trae/agents/dispatcher-agent.md

## 核心内容

### 智能体 ID
`dispatcher_agent`

### 核心职责
协调、分发、博弈调度、智能路由、负载均衡

### 核心能力
- 任务识别任务类型
- 选择最优智能体
- 博弈决策
- 情绪识别与响应适配
- 与 6A 工作流整合

### 任务类型映射
| 任务关键词 | 调度智能体 |
|------------|-----------|
| 代码、写代码、debug | code_executor_agent |
| 规则、规范、解释 | rule_interpreter_agent |
| 文档、README、写文档 | writer_agent |
| 执行、命令、搜索 | tool_agent |
| 需求、澄清 | user_proxy_agent |
| wiki、知识、编译 | llm_wiki_agent |
| 协调、调度、复杂、多步骤 | dispatcher_agent |

## 相关链接
- [[6A 项目管理工作流]]
- [[情绪感知与响应适配]]
- [[智能体团队]]

## 标签
#concepts #agents #dispatcher
