# LLM Wiki知识编译范式

## 核心信息
- 创建日期：2026-05-23
- 最后更新：2026-05-23
- 来源：Karpathy的GitHub Gist + 调研资料

## 核心内容

### 核心理念
**Compile, don't retrieve** - 知识编译而不是检索
- 不要让LLM在查询时去理解原始文档
- 提前让LLM把文档"编译"成结构化的知识

### 三层架构
1. **Schema层**：行为契约（AGENTS.md）
2. **Wiki层**：已编译的知识图谱（Markdown文件）
3. **Raw Sources层**：原始资料（只读）

### 核心操作
- **Ingest**：摄入-编译原始资料
- **Query**：查询-读取已编译知识
- **Lint**：校验-维护wiki质量

### 页面类型
- **Entities**：人物、组织、项目
- **Concepts**：技术概念、理论
- **Summaries**：原始资料摘要
- **Synthesis**：综合分析、对比
- **Queries**：常见问题答案

## 相关链接
- [[andrej-karpathy]] - LLM Wiki的提出者
- [[rag]] - 传统RAG对比
- [[rag-vs-llm-wiki]] - 详细对比分析
- [[how-to-use-llm-wiki]] - 使用指南

## 标签
#概念 #llm-wiki #知识编译 #karpathy
