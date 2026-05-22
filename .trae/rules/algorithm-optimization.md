# 算法优化规范 (L3)

**版本**: v1.0 | **更新日期**: 2026-05-21 | **规则状态**: ✅ 生效中
**触发条件**: 性能优化、智能决策、算法应用场景
**L1支撑**: 算法智能模块 [L1-13]
**L2支撑**: 算法规范 [L2-13.1]

---

## 一、缓存算法 [L3-13.1.1]

### 1.1 LRU Cache（最近最少使用缓存）

**用途**: 减少重复API调用，提升响应速度

**实现规范**:
| 参数 | 默认值 | 说明 |
|------|-------|------|
| max_size | 1000 | 最大缓存条目数 |
| ttl | 3600 | 缓存生存时间（秒） |

**算法逻辑**:
```python
class LRUCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self._cache = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)
        return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)
```

**应用场景**:
- 重复的Prompt模板缓存
- 频繁查询的规则文件内容
- 相似任务的结果缓存

### 1.2 Prompt Cache（提示缓存）

**用途**: 存储常用指令模板，减少Token消耗

**缓存策略**:
| 策略 | 触发条件 | 缓存时长 |
|------|---------|---------|
| 完整匹配 | 相同Prompt | 30分钟 |
| 部分匹配 | 相似度>0.9 | 15分钟 |
| 前缀匹配 | 共同前缀>50字符 | 10分钟 |

---

## 二、向量匹配算法 [L3-13.2.1]

### 2.1 Cosine Similarity（余弦相似度）

**用途**: 语义路由、意图识别、相似任务匹配

**算法实现**:
```python
class VectorMatcher:
    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        n1 = math.sqrt(sum(a * a for a in v1))
        n2 = math.sqrt(sum(b * b for b in v2))
        return dot / (n1 * n2) if n1 and n2 else 0.0

    @staticmethod
    def vectorize(text: str, model: str = "default") -> List[float]:
        # 向量化实现（使用本地模型或API）
        pass
```

**相似度阈值**:
| 匹配等级 | 相似度范围 | 动作 |
|---------|-----------|------|
| 精确匹配 | ≥0.95 | 直接复用 |
| 高相似 | 0.85-0.95 | 轻度调整 |
| 中相似 | 0.70-0.85 | 重新生成 |
| 低相似 | <0.70 | 全新处理 |

### 2.2 语义路由应用

**路由流程**:
```
用户输入 → 向量化 → 相似度匹配 → 选择最优策略
                           ↓
              ┌────────────┼────────────┐
              ↓            ↓            ↓
           精确匹配      高相似       低相似
           (直接复用)   (调整后用)   (新建)
```

---

## 三、意图识别算法 [L3-13.3.1]

### 3.1 关键词匹配

**用途**: 快速识别用户意图类型

**关键词库**:
```python
INTENT_KEYWORDS = {
    "code": ["写代码", "debug", "修复", "代码", "程序"],
    "design": ["设计", "架构", "方案", "蓝图"],
    "review": ["审核", "检查", "审查", "评估"],
    "research": ["调研", "研究", "分析", "调查"],
    "optimize": ["优化", "改进", "提升", "性能"],
    "token_save": ["省钱", "节省", "减少", "降低成本"]
}
```

### 3.2 向量匹配（双重验证）

**意图识别流程**:
```python
class IntentRecognizer:
    def recognize(self, text: str) -> str:
        # 第一层：关键词快速匹配
        keyword_intent = self._keyword_match(text)
        
        # 第二层：向量相似度验证
        vector_intent = self._vector_match(text)
        
        # 综合判断
        if keyword_intent == vector_intent:
            return keyword_intent
        scores = {
            keyword_intent: 0.6,
            vector_intent: 0.4
        }
        return max(scores, key=scores.get)
```

---

## 四、博弈决策算法 [L3-13.4.1]

### 4.1 最小最大算法（Minimax）

**用途**: 方案对比、冲突解决、多方博弈

**算法结构**:
```python
def minimax(node: Node, depth: int, maximizing_player: bool) -> float:
    if depth == 0 or node.is_terminal():
        return node.evaluate()
    
    if maximizing_player:
        value = float('-inf')
        for child in node.get_children():
            value = max(value, minimax(child, depth - 1, False))
        return value
    else:
        value = float('inf')
        for child in node.get_children():
            value = min(value, minimax(child, depth - 1, True))
        return value
```

**应用场景**:
- 方案A vs 方案B 的最优选择
- 多智能体资源竞争
- 冲突的解决方案评估

### 4.2 纳什均衡（Nash Equilibrium）

**用途**: 多方博弈场景下的稳定策略

**决策矩阵**:
```python
def nash_equilibrium(payoff_matrix: List[List[float]]) -> Tuple[int, int]:
    # 求解纳什均衡点
    rows, cols = len(payoff_matrix), len(payoff_matrix[0])
    best_row, best_col = 0, 0
    
    for i in range(rows):
        for j in range(cols):
            # 检查是否为帕累托最优
            if payoff_matrix[i][j] > payoff_matrix[best_row][best_col]:
                best_row, best_col = i, j
    
    return best_row, best_col
```

---

## 五、自适应学习算法 [L3-13.5.1]

### 5.1 成功率反馈机制

**用途**: 规则优化、自我改进、模式识别

**反馈系统**:
```python
class AdaptiveLearning:
    def __init__(self, window_size: int = 10):
        self._history = []
        self._window_size = window_size
        self._success_threshold = 0.6
        self._adjustment_step = 1

    def record(self, result: Dict) -> None:
        self._history.append(result.get('status') == 'success')
        if len(self._history) > self._window_size:
            self._history.pop(0)

    def get_success_rate(self) -> float:
        if not self._history:
            return 0.0
        return sum(self._history) / len(self._history)

    def should_adjust(self) -> bool:
        rate = self.get_success_rate()
        return rate < self._success_threshold
```

### 5.2 自动调整策略

**调整规则**:
| 当前成功率 | 蜂群规模 | 调整动作 |
|-----------|---------|---------|
| <60% | <10 | 规模+1 |
| >90% | >3 | 规模-1 |
| 60%-90% | 3-10 | 保持 |

---

## 六、算法调用优先级 [L3-13.6.1]

| 优先级 | 算法类型 | 触发场景 | 性能目标 |
|-------|---------|---------|---------|
| P0 | 缓存命中 | 重复请求 | <10ms |
| P1 | 向量匹配 | 意图识别 | <50ms |
| P2 | 博弈决策 | 方案对比 | <100ms |
| P3 | 自适应学习 | 规则优化 | 后台执行 |

---

## 七、版本历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0 | 2026-05-21 | 初始版本，定义算法优化具体实现 | 系统 |
