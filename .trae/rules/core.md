# L3 核心规则 - core.md

> 中央调度、智能路由、博弈模式的核心实现

---

## 1. 中央调度引擎（L3-R001）

### 1.1 强耦合架构

| 组件 | 作用 | 耦合方式 |
|------|------|---------|
| AgentRegistry | 智能体注册中心 | 直接引用 |
| AgentCallInterface | 智能体调用接口 | 同步执行 |
| MessageBus | 消息总线 | 异步执行 |

### 1.2 双模式执行

| 模式 | 触发条件 | 执行方式 |
|------|----------|----------|
| **同步模式** | 默认 | AgentCallInterface直接调用 |
| **异步模式** | 消息总线 | MessageBus异步消息传递 |

### 1.3 调度流程

```
用户任务 → 博弈模式检测 → 智能体选择
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
        同步模式                   异步模式
     (AgentCallInterface)       (MessageBus)
              ↓                         ↓
              └────────────┬────────────┘
                           ↓
                      结果聚合
```

---

## 2. 智能路由引擎（L3-R002）

### 2.1 路由策略

| 策略 | 优先级 |
|-----|-------|
| 向量相似度路由 | 最高 |
| 语义意图路由 | 最高 |
| 上下文路由 | 高 |
| 负载路由 | 中 |
| 故障转移路由 | 高 |

### 2.2 意图识别

| 意图类型 | 触发关键词 |
|----------|-----------|
| code | 写代码、debug |
| design | 设计、架构 |
| review | 审核、检查 |
| research | 调研、研究 |
| general | 其他 |

### 2.3 向量匹配

```python
class VectorMatcher:
    @staticmethod
    def cosine_similarity(v1, v2):
        dot = sum(a*b for a,b in zip(v1,v2))
        n1 = math.sqrt(sum(a*a for a in v1))
        n2 = math.sqrt(sum(b*b for b in v2))
        return dot/(n1*n2) if n1 and n2 else 0.0
```

---

## 3. 博弈模式（L3-R003）

### 3.1 模式类型

| 模式 | 触发词 | 流程 | 最大迭代 |
|------|-------|------|----------|
| 辩论模式 | 对比、权衡、优缺点 | 视角A→视角B→裁决 | 3次 |
| 优化改进 | 优化、改进、重构 | 生成→挑剔→融合 | 3次 |
| 深度设计 | 设计、架构、方案 | 蓝图→挑战→融合 | 5次 |
| 协商决策 | 协商、讨论、共识 | 提案→评估→投票→决策 | - |
| 资源拍卖 | 分配、竞争、优先级 | 竞价→评估→分配 | - |

### 3.2 博弈流程

```
子功能调研
    ↓
【生成阶段】生成3-5个候选解决方案
    ↓
【博弈阶段】每个方案经过：
    ├── 拥护者辩护
    ├── 挑剔者质疑
    └── 成本分析
    ↓
【裁决阶段】用户选择最优方案
    ↓
【执行阶段】实施选定方案
```

### 3.3 解决方案评估矩阵

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 功能完整性 | 25% | 解决问题程度 |
| 实现复杂度 | 20% | 越简单越好 |
| 风险程度 | 20% | 风险越低越好 |
| 扩展性 | 15% | 未来适应能力 |
| 性能影响 | 10% | 对系统性能影响 |
| 维护成本 | 10% | 长期维护难度 |

---

## 4. 任务分诊台（L3-R004）

### 4.1 任务识别

```python
def recognize_task(user_input):
    tokens = segment(user_input)
    intent = intent_recognizer.recognize(tokens)
    concepts = knowledge_graph.query(tokens)
    return {"tokens": tokens, "intent": intent, "concepts": concepts}
```

### 4.2 智能路由策略

| 策略 | 优先级 | 实现逻辑 |
|------|--------|---------|
| 连续同类任务复用 | P0 | 检查上下文，复用最近成功的智能体组合 |
| 用户偏好优先 | P0 | 读取用户偏好配置，优先使用偏好智能体 |
| 失败切换 | P0 | 任务失败时自动切换备用智能体 |
| 语义路由 | P1 | 新任务进行语义匹配，选择最佳智能体 |

### 4.3 执行流程

```
用户输入
    ↓
【Step 1】任务识别
    ↓
【Step 2】智能路由
    ↓
【Step 3】模式选择
    ↓
【Step 4】并行执行
    ↓
【Step 5】结果聚合
    ↓
返回用户
```

---

## 5. 执行任务评估（L3-R005）

### 5.1 评估指标

| 指标 | 说明 | 权重 |
|------|------|------|
| 成功率 | 任务成功完成的比例 | 40% |
| 响应时间 | 平均响应时间 | 30% |
| 资源消耗 | CPU/内存消耗 | 20% |
| 用户反馈 | 用户评价 | 10% |

### 5.2 置信度评估

| 范围 | 状态 | 处理 |
|------|------|------|
| ≥95% | 高置信 | 直接执行 |
| 85%-95% | 中等置信 | 提示后执行 |
| 70%-85% | 低置信 | 确认后执行 |
| <70% | 不可靠 | 拒绝或降级 |

---

## 6. 蜂群协作（L3-R006）

### 6.1 去中心化决策

```python
class DecentralizedDecisionMaker:
    def make_decision(self, options, context):
        scores = [self._local_evaluate(options, context)]
        scores += self._collect_neighbor_scores(options, context)
        return self._weighted_vote(options, scores)

    def _weighted_vote(self, options, all_scores):
        weights = [0.5] + [0.1] * len(all_scores[1:])
        totals = [0.0] * len(options)
        for s, w in zip(all_scores, weights):
            for i, x in enumerate(s): totals[i] += x * w
        return options[totals.index(max(totals))]
```

### 6.2 信息素传递

```python
class PheromoneSystem:
    def __init__(self, decay=0.1): self._p, self._decay = {}, decay
    def deposit(self, k, v): self._p[k] = self._p.get(k, 0) + v
    def evaporate(self):
        for k in list(self._p.keys()):
            self._p[k] *= (1 - self._decay)
            if self._p[k] < 0.01: del self._p[k]
    def get(self, k): return self._p.get(k, 0)
```

---

## 7. 工具优先原则（L3-R007）

### 7.1 工具分类

| 类型 | 说明 | 优先级 |
|------|------|--------|
| 系统工具 | 文件、终端等 | 最高 |
| 第三方工具 | MCP、外部API | 高 |
| 智能体工具 | 其他智能体 | 中 |
| 语言模型 | 纯文本输出 | 低 |

### 7.2 工具选择原则

1. 优先使用系统工具
2. 避免重复造轮子
3. 权衡工具效率和准确性

---

## 8. 内置备用规则（L3-R008）

### 8.1 降级策略

| 故障类型 | 处理策略 |
|---------|---------|
| 单个智能体失败 | 自动切换邻居 |
| 网络分区 | 本地继续执行 |
| 消息总线故障 | 回退同步模式 |

### 8.2 熔断规则

```python
CIRCUIT_BREAKER_STATES = {
    "closed": {"failure_threshold": 5, "timeout": 30000},
    "open": {"recovery_timeout": 60000},
    "half_open": {"success_threshold": 3}
}
```

---

## 9. 插件化加载器（L3-R009）

### 9.1 插件接口

```python
class IAgent(ABC):
    @abstractmethod
    def get_id(self) -> str: pass
    @abstractmethod
    async def execute(self, task, context) -> Dict: pass
    @abstractmethod
    async def health_check(self) -> bool: pass
```

### 9.2 状态管理

| 状态类型 | 值 |
|---------|---|
| runtime | busy/idle/error |
| config | timeout/retry_limit |
| performance | load/response_time |
| monitoring | active/inactive |

---

**版本**: v4.0 | **日期**: 2026-05-15 | **行数**: ~300行