---
name: evolution-analyzer
description: 自主进化调研分析模块，支持调研最佳实践、多维度对比分析、缺陷检测与自动净化
version: 1.0.0
author: Evolution Team
tags: ["evolution", "research", "analysis", "optimization", "auto-improvement"]
---

# Evolution Analyzer 自主进化调研分析模块 v1.0

## 功能描述

自主进化调研分析模块，实现完整的**调研→分析→对比→净化**流程。

### 核心功能
- 🔍 **调研引擎**：全网调研最佳实践、记录信源信息
- 📊 **分析引擎**：多维度对比分析、打分卡评估
- 🐛 **缺陷检测**：检查子模块功能缺陷
- 🚀 **自动优化**：根据调研和缺陷分析结果自动净化

---

## 模块架构

```
evolution-analyzer/
├── __init__.py              # 模块初始化
├── researcher.py            # 调研引擎
├── analyzer.py              # 分析引擎
├── defect_detector.py       # 缺陷检测器
└── optimizer.py             # 自动优化器
```

---

## 使用说明

### 1. 调研最佳实践

```python
from evolution_analyzer import ResearchEngine

engine = ResearchEngine()

# 添加调研信源
engine.add_source(
    url="https://github.com/example/best-practice",
    title="多智能体系统最佳实践",
    summary="介绍了多智能体系统的架构设计和最佳实践",
    author="Anthropic",
    accessed_at="2026-05-15"
)

# 获取调研总结
summary = engine.get_research_summary()
print(f"信源数量：{summary['total_sources']}")
print(f"高可信度信源：{summary['high_credibility_count']}")

# 导出调研报告
engine.export_to_markdown("research_report.md")
```

### 2. 多维度对比分析

```python
from evolution_analyzer import AnalysisEngine

engine = AnalysisEngine()

# 评估当前系统
current_eval = engine.evaluate(
    system_name="当前体系",
    criteria={
        "架构完整性": 75.0,
        "安全机制": 80.0,
        "可扩展性": 70.0,
        "鲁棒性": 65.0,
        "实用性": 85.0,
        "可维护性": 90.0
    }
)

# 评估调研体系
researched_eval = engine.evaluate(
    system_name="调研体系",
    criteria={
        "架构完整性": 90.0,
        "安全机制": 85.0,
        "可扩展性": 88.0,
        "鲁棒性": 82.0,
        "实用性": 87.0,
        "可维护性": 85.0
    }
)

# 对比分析
comparison = engine.compare([current_eval, researched_eval])
print(f"最佳系统：{comparison['best_system']['system_name']}")
print(f"平均得分：{comparison['average_score']:.1f}")

# 生成对比表格
md_table = engine.generate_comparison_table(comparison)
print(md_table)
```

### 3. 缺陷检测

```python
from evolution_analyzer import DefectDetector

detector = DefectDetector()

# 检测模块缺陷
defects = detector.detect("c:/path/to/module")

# 获取缺陷报告
report = detector.generate_report()
print(f"总缺陷数：{report['total_defects']}")
print(f"严重缺陷：{len(report['critical_defects'])}")
print(f"高级缺陷：{len(report['high_defects'])}")

# 导出缺陷报告
detector.export_to_markdown("defect_report.md")
```

### 4. 自动优化

```python
from evolution_analyzer import AutoOptimizer

optimizer = AutoOptimizer()

# 生成优化提案
proposal = optimizer.generate_proposal(
    research_summary=research_summary,
    comparison_report=comparison_report,
    defect_report=defect_report
)

# 保存提案
optimizer.save_proposal(proposal, status="pending")

# 生成优化报告
report_md = optimizer.generate_optimization_report(proposal)
print(report_md)

# 导出报告
optimizer.export_report(proposal, "optimization_report.md")
```

---

## 评估维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 架构完整性 | 25% | 三层架构、模块化程度 |
| 安全机制 | 20% | 安全铁律、漏洞防护 |
| 可扩展性 | 15% | 松耦合、插件化支持 |
| 鲁棒性 | 15% | 故障恢复、降级策略 |
| 实用性 | 15% | 实际项目应用、社区验证 |
| 可维护性 | 10% | 文档完善、规则清晰 |

---

## 打分标准

| 分数 | 等级 | 说明 |
|------|------|------|
| 90-100 | 卓越 | 强烈建议采纳 |
| 80-89 | 优秀 | 建议采纳 |
| 70-79 | 良好 | 可选采纳 |
| 60-69 | 一般 | 需要评估 |
| <60 | 需改进 | 不建议采纳 |

---

## 缺陷严重程度

| 级别 | 说明 | 处理策略 |
|------|------|---------|
| Critical | 严重缺陷 | 立即修复 |
| High | 高级缺陷 | 优先修复 |
| Medium | 中级缺陷 | 计划修复 |
| Low | 低级缺陷 | 可选修复 |

---

## 输出格式

### 调研报告
- Markdown 格式
- 包含所有信源信息
- 可信度评估
- 核心发现总结

### 对比报告
- 多维度打分卡
- 对比表格
- 最佳实践识别
- 改进建议

### 缺陷报告
- 缺陷分类统计
- 严重程度分布
- 详细缺陷列表
- 修复建议

### 优化提案
- 提案 ID 和时间戳
- 调研总结
- 对比分析结果
- 缺陷报告
- 优化建议列表
- 行动项列表

---

## 工作流程

```
用户请求
    ↓
调研引擎 → 收集最佳实践
    ↓
分析引擎 → 多维度对比评估
    ↓
缺陷检测 → 检查功能缺陷
    ↓
自动优化 → 生成优化提案
    ↓
用户审批 → 批准/拒绝/修改
    ↓
执行优化 → 自动/手动修复
    ↓
记录存档 → 提案和决策记录
```

---

## 触发条件

- 用户请求自主进化调研
- 定期进化检查（1-2 天）
- 系统性能下降检测
- 新功能开发前的最佳实践调研
- 代码质量审查

---

## 与自主进化机制的关系

本模块实现了 [自主进化机制_v1.0.md](../../rules/core/自主进化机制_v1.0.md) 中定义的核心流程：

1. ✅ **全网调研流程** - ResearchEngine
2. ✅ **对比评估机制** - AnalysisEngine
3. ✅ **缺陷检测** - DefectDetector
4. ✅ **更新提案生成** - AutoOptimizer

---

## 示例输出

### 对比表格示例

```markdown
| 维度 | 当前体系 | 调研体系 | 差异 |
|------|----------|----------|------|
| 架构完整性 | 75.0 | 90.0 | +15.0 |
| 安全机制 | 80.0 | 85.0 | +5.0 |
| 可扩展性 | 70.0 | 88.0 | +18.0 |
| 鲁棒性 | 65.0 | 82.0 | +17.0 |
| 实用性 | 85.0 | 87.0 | +2.0 |
| 可维护性 | 90.0 | 85.0 | -5.0 |

**综合得分**
- 当前体系：77.5 分
- 调研体系：86.7 分
- 提升幅度：+9.2 分
```

---

## 配置选项

```python
# 自定义评估维度
custom_dimensions = [
    EvaluationDimension("性能", 0.30, "响应时间、吞吐量"),
    EvaluationDimension("成本", 0.25, "Token 消耗、计算资源"),
    # ...
]

engine = AnalysisEngine(dimensions=custom_dimensions)
```

---

## 版本历史

| 版本 | 更新内容 |
|------|---------|
| v1.0.0 | 初始版本，实现调研→分析→对比→净化完整流程 |

---

**版本**: v1.0.0 | **日期**: 2026-05-15 | **功能**: 自主进化调研分析
