# Token优化规范 (L3)

**版本**: v1.0 | **更新日期**: 2026-05-21 | **规则状态**: ✅ 生效中
**触发条件**: API调用、Token消耗、成本优化场景
**L1支撑**: Token优化模块 [L1-14]
**L2支撑**: Token优化规范 [L2-13.2]

---

## 一、Prompt缓存策略 [L3-14.1.1]

### 1.1 缓存层级

| 层级 | 缓存内容 | 节省比例 | 命中率目标 |
|------|---------|---------|-----------|
| L1 | 完整Prompt模板 | 40-50% | 30% |
| L2 | Prompt前缀模式 | 25-35% | 45% |
| L3 | 指令结构缓存 | 15-25% | 25% |

### 1.2 缓存实现

```python
class PromptCache:
    def __init__(self):
        self._exact_cache = LRUCache(max_size=500, ttl=1800)
        self._prefix_cache = LRUCache(max_size=1000, ttl=900)
        self._structure_cache = LRUCache(max_size=2000, ttl=600)

    def get_cached_prompt(self, prompt: str) -> Optional[Dict]:
        # 精确匹配
        exact = self._exact_cache.get(prompt)
        if exact:
            return {"type": "exact", "prompt": exact, "savings": 0.45}

        # 前缀匹配
        for cached_prompt in self._prefix_cache._cache.keys():
            if prompt.startswith(cached_prompt):
                ratio = len(cached_prompt) / len(prompt)
                if ratio > 0.5:
                    return {"type": "prefix", "prompt": cached_prompt,
                            "suffix": prompt[len(cached_prompt):], "savings": 0.30}

        return None

    def cache_prompt(self, prompt: str, response: str) -> None:
        self._exact_cache.set(prompt, response)
        # 提取前缀
        prefix = self._extract_common_prefix(prompt)
        if prefix:
            self._prefix_cache.set(prefix, True)
```

### 1.3 缓存命中处理

```python
def handle_cache_hit(cache_result: Dict, original_prompt: str) -> str:
    if cache_result["type"] == "exact":
        return cache_result["prompt"]
    elif cache_result["type"] == "prefix":
        return cache_result["prompt"] + cache_result["suffix"]
    return original_prompt
```

---

## 二、响应压缩策略 [L3-14.2.1]

### 2.1 压缩方法

| 方法 | 节省比例 | 适用场景 | 实现难度 |
|------|---------|---------|---------|
| Markdown精简 | 10-15% | 所有响应 | 低 |
| 冗余去除 | 5-10% | 长响应 | 低 |
| 格式化优化 | 5-8% | 代码输出 | 中 |

### 2.2 压缩实现

```python
class ResponseCompressor:
    @staticmethod
    def compress(response: str) -> str:
        lines = response.split('\n')
        compressed = []
        prev_empty = False
        
        for line in lines:
            stripped = line.strip()
            # 去除多余空行
            if not stripped:
                if not prev_empty:
                    compressed.append('')
                    prev_empty = True
                continue
            prev_empty = False
            # 去除行尾空格
            compressed.append(stripped)
        
        result = '\n'.join(compressed)
        # 去除多余标记
        result = re.sub(r'[#*]{3,}', '', result)
        return result

    @staticmethod
    def estimate_tokens(text: str) -> int:
        # 粗略估算：中文按字符计，英文按单词计
        return len(text) // 2
```

### 2.3 智能摘要

```python
class SmartSummarizer:
    def __init__(self, max_tokens: int = 500):
        self._max_tokens = max_tokens

    def summarize_if_needed(self, response: str) -> str:
        estimated = self.estimate_tokens(response)
        if estimated <= self._max_tokens:
            return response
        
        # 按段落保留关键信息
        paragraphs = response.split('\n\n')
        summary = []
        tokens_used = 0
        
        for para in paragraphs:
            para_tokens = self.estimate_tokens(para)
            if tokens_used + para_tokens <= self._max_tokens * 0.8:
                summary.append(para)
                tokens_used += para_tokens
        
        return '\n\n'.join(summary) + f"\n\n[已压缩，原{estimated} tokens]"
```

---

## 三、智能批量策略 [L3-14.3.1]

### 3.1 批量合并规则

| 任务类型 | 合并条件 | 最大批量 |
|---------|---------|---------|
| 同类型任务 | 相同智能体 | 5个 |
| 相关任务 | 共享上下文 | 3个 |
| 独立任务 | 无依赖 | 2个 |

### 3.2 批量执行

```python
class BatchOptimizer:
    def should_batch(self, tasks: List[Dict]) -> bool:
        if len(tasks) < 2:
            return False
        
        # 检查任务相似度
        types = [t.get('type') for t in tasks]
        return len(set(types)) == 1

    def create_batch_prompt(self, tasks: List[Dict]) -> str:
        template = "请依次处理以下{count}个任务：\n"
        for i, task in enumerate(tasks, 1):
            template += f"\n任务{i}：{task['description']}"
            if task.get('constraints'):
                template += f"\n约束：{task['constraints']}"
        return template

    def split_batch_response(self, response: str, count: int) -> List[str]:
        # 按任务数量分割响应
        parts = []
        lines = response.split('\n')
        current = []
        for line in lines:
            if line.strip().startswith('任务') and len(parts) < count - 1:
                if current:
                    parts.append('\n'.join(current))
                    current = []
            current.append(line)
        if current:
            parts.append('\n'.join(current))
        return parts if len(parts) == count else [response]
```

---

## 四、上下文精简策略 [L3-14.4.1]

### 4.1 精简规则

| 对话阶段 | 保留内容 | 精简比例 |
|---------|---------|---------|
| 早期对话 | 全部 | 0% |
| 中期对话 | 关键决策+当前状态 | 40% |
| 后期对话 | 最新10轮+决策摘要 | 60% |

### 4.2 上下文窗口管理

```python
class ContextManager:
    def __init__(self, max_tokens: int = 4000):
        self._max_tokens = max_tokens
        self._decisions = []
        self._state = {}

    def should_compress(self, conversation: List[Dict]) -> bool:
        total = sum(self.estimate_tokens(m['content']) for m in conversation)
        return total > self._max_tokens * 0.8

    def compress_context(self, conversation: List[Dict]) -> List[Dict]:
        if len(conversation) <= 10:
            return conversation
        
        compressed = conversation[-10:]
        summary = self._generate_summary(conversation[:-10])
        
        return [
            {"role": "system", "content": f"[早期对话摘要]\n{summary}"}
        ] + compressed

    def _generate_summary(self, old_messages: List[Dict]) -> str:
        # 提取关键信息
        decisions = [m for m in old_messages if m.get('is_decision')]
        state_updates = [m for m in old_messages if m.get('is_state_update')]
        
        summary = "【早期关键决策】\n"
        summary += "\n".join(f"- {d['content']}" for d in decisions[-5:]) or "无"
        summary += "\n\n【状态更新】\n"
        summary += "\n".join(f"- {s['content']}" for s in state_updates[-5:]) or "无"
        
        return summary
```

---

## 五、向量缓存策略 [L3-14.5.1]

### 5.1 向量存储优化

| 缓存类型 | 存储内容 | 节省比例 | TTL |
|---------|---------|---------|-----|
| 完全相同 | 相同文本的向量 | 60% | 1小时 |
| 相似文本 | 相似度>0.9的向量 | 40% | 30分钟 |
| 前缀向量 | 公共前缀的向量 | 30% | 15分钟 |

### 5.2 向量缓存实现

```python
class VectorCache:
    def __init__(self):
        self._exact_vectors = LRUCache(max_size=5000, ttl=3600)
        self._prefix_vectors = LRUCache(max_size=10000, ttl=1800)

    def get_vector(self, text: str) -> Optional[List[float]]:
        # 精确匹配
        vec = self._exact_vectors.get(text)
        if vec:
            return vec
        
        # 前缀匹配
        for cached, vec in self._prefix_vectors._cache.items():
            if text.startswith(cached):
                return vec
        
        return None

    def cache_vector(self, text: str, vector: List[float]) -> None:
        self._exact_vectors.set(text, vector)
        
        # 缓存前缀
        for i in range(20, min(len(text), 100), 20):
            prefix = text[:i]
            if prefix not in self._prefix_vectors._cache:
                self._prefix_vectors.set(prefix, vector)
```

---

## 六、智能重试策略 [L3-14.6.1]

### 6.1 重试机制

| 错误类型 | 重试次数 | 间隔策略 | Token节省 |
|---------|---------|---------|---------|
| 速率限制 | 3 | 指数退避 | 15% |
| 超时 | 2 | 线性递增 | 10% |
| 服务器错误 | 2 | 固定等待 | 12% |

### 6.2 智能重试实现

```python
class SmartRetry:
    def __init__(self):
        self._retry_counts = {}
        self._backoff = {1: 1, 2: 2, 3: 5}

    def should_retry(self, error: str, attempt: int) -> bool:
        if attempt > 3:
            return False
        
        retryable = ["rate_limit", "timeout", "server_error"]
        return any(e in error.lower() for e in retryable)

    def get_wait_time(self, attempt: int) -> int:
        return self._backoff.get(attempt, 5)

    def estimate_retry_savings(self, attempts: int) -> float:
        # 估算重试vs新建的成本比
        return 1 - (attempts / (attempts + 1))
```

---

## 七、Token节省汇总 [L3-14.7.1]

### 7.1 各策略节省比例

| 策略 | 单独节省 | 组合节省 | 实现优先级 |
|------|---------|---------|-----------|
| Prompt缓存 | 30-50% | 35-55% | P0 |
| 向量缓存 | 40-60% | 45-65% | P0 |
| 响应压缩 | 10-20% | 15-25% | P1 |
| 智能批量 | 20-40% | 25-45% | P1 |
| 上下文精简 | 15-30% | 20-35% | P2 |
| 智能重试 | 10-15% | 12-18% | P2 |

### 7.2 综合节省估算

```python
def estimate_total_savings(enabled_strategies: List[str]) -> Dict:
    base_savings = {
        "Prompt缓存": 0.40,
        "向量缓存": 0.50,
        "响应压缩": 0.15,
        "智能批量": 0.30,
        "上下文精简": 0.22,
        "智能重试": 0.12
    }
    
    # 组合折扣（策略越多，组合效应越大）
    count = len(enabled_strategies)
    combo_discount = 1 + (count * 0.05)
    
    individual = sum(base_savings.get(s, 0) for s in enabled_strategies)
    combined = min(individual * combo_discount, 0.85)
    
    return {
        "individual_savings": f"{individual * 100:.0f}%",
        "combined_savings": f"{combined * 100:.0f}%",
        "strategies_count": count
    }
```

---

## 八、版本历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0 | 2026-05-21 | 初始版本，定义Token优化具体实现 | 系统 |
