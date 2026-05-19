---
name: "api-token-optimizer"
description: "API Token优化技能，涵盖缓存、限流、轮询、优雅降级、Prompt缓存、Few-shot精选等全面策略。Invoke when user needs to optimize API calls, reduce token consumption, or implement rate limiting."
---

# API Token Optimizer v2.0

Comprehensive skill for maximizing API token/quota savings across programming scenarios (GitHub, OpenAI, AWS, etc.).

## 核心优化维度

### 1. 身份与配额管理 (Identity & Quota Management)

#### 多Token轮询策略
```python
from typing import List, Optional
from datetime import datetime, timedelta
import time

class TokenPool:
    def __init__(self, tokens: List[dict]):
        self.tokens = tokens  # [{"token": "xxx", "rate_limit": 5000, "remaining": 5000, "reset_at": timestamp}]

    def get_healthy_token(self) -> Optional[dict]:
        """获取健康的token，优先选择剩余配额多的"""
        now = time.time()
        healthy = [t for t in self.tokens if t["remaining"] > 0 and t["reset_at"] <= now]
        if not healthy:
            return None
        return max(healthy, key=lambda x: x["remaining"])

    def rotate(self, exhausted_token: str):
        """标记token耗尽，切换到下一个"""
        for t in self.tokens:
            if t["token"] == exhausted_token:
                t["remaining"] = 0
```

#### 智能熔断机制
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=30):
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True  # HALF_OPEN
```

### 2. 请求复用与缓存 (Cache & Reuse)

#### LRU内存缓存
```python
from functools import lru_cache
from datetime import datetime, timedelta
import hashlib
import json

class TimedLRUCache:
    def __init__(self, max_size=100, ttl_seconds=300):
        self.cache = {}
        self.timestamps = {}
        self.max_size = max_size
        self.ttl = ttl_seconds

    def _is_expired(self, key: str) -> bool:
        if key not in self.timestamps:
            return True
        return (datetime.now() - self.timestamps[key]).total_seconds() > self.ttl

    def get(self, key: str):
        if key in self.cache and not self._is_expired(key):
            return self.cache[key]
        return None

    def set(self, key: str, value):
        if len(self.cache) >= self.max_size:
            oldest = min(self.timestamps.keys(), key=lambda k: self.timestamps[k])
            del self.cache[oldest]
            del self.timestamps[oldest]
        self.cache[key] = value
        self.timestamps[key] = datetime.now()
```

#### HTTP条件请求 (ETag/If-None-Match)
```python
import requests

def conditional_request(url: str, headers: dict = None, etag: str = None):
    """利用ETag实现304 Not Modified缓存"""
    req_headers = headers or {}
    if etag:
        req_headers["If-None-Match"] = etag

    response = requests.get(url, headers=req_headers)

    if response.status_code == 304:
        return {"cached": True, "etag": etag}

    new_etag = response.headers.get("ETag")
    return {
        "cached": False,
        "data": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text,
        "etag": new_etag
    }
```

### 3. 调用策略优化 (Calling Strategy)

#### Webhook替代轮询
```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = "your-secret-key"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Signature', '')
    payload = request.get_data()

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        return jsonify({"error": "Invalid signature"}), 401

    event = request.headers.get('X-Event-Type')
    data = request.get_json()

    if event == 'push':
        handle_push(data)
    elif event == 'pull_request':
        handle_pr(data)

    return jsonify({"status": "ok"})
```

#### 增量获取算法
```python
def incremental_fetch(api_func, params: dict, since_id: int = None, per_page: int = 100):
    """
    增量获取数据，避免重复拉取全量
    """
    all_items = []
    page = 1
    last_id = since_id or 0

    while True:
        response = api_func(
            **params,
            since_id=last_id,
            per_page=per_page,
            page=page
        )

        items = response.get('items', [])
        if not items:
            break

        all_items.extend(items)
        last_id = items[-1]['id']

        if len(items) < per_page:
            break
        page += 1

    return all_items
```

### 4. 架构与降级 (Architecture & Degradation)

#### API优化代理网关架构
```
┌─────────────────────────────────────────────────────────────┐
│                    API Optimization Gateway                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │  Cache  │    │  Rate   │    │  Token  │    │Fallback │  │
│  │  Layer  │───▶│  Limit  │───▶│  Router │───▶│  Layer  │  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### 优雅降级策略
```python
class GracefulDegradation:
    def __init__(self, cache_layer):
        self.cache = cache_layer

    def get_with_fallback(self, key: str, primary_func, fallback_data=None):
        """
        当API不可用时，返回缓存数据或静态兜底数据
        """
        cached = self.cache.get(key)
        if cached:
            return {"source": "cache", "data": cached}

        try:
            data = primary_func()
            self.cache.set(key, data)
            return {"source": "api", "data": data}
        except APIError as e:
            if fallback_data:
                return {"source": "fallback", "data": fallback_data}
            raise e
```

---

## v2.0 新增高级优化策略

### 5. Prompt Caching（提示缓存）

OpenAI 风格的提示缓存，缓存超过 1024 tokens 的提示，节省高达 80% 成本。

```python
from advanced_strategies import PromptCache

cache = PromptCache(cache_threshold=1024, ttl_seconds=3600)

# 缓存响应
cache.set(prompt, {"result": "success"})

# 获取缓存（命中返回None表示未命中）
cached = cache.get(prompt)
if cached:
    print("缓存命中!")
```

**效果**：Token 节省高达 90%，响应时间降低 80%

### 6. Few-shot 精选示例

语义相似度选择最相关的 Few-shot 示例，减少 token 消耗同时保持准确性。

```python
from advanced_strategies import FewShotSelector

examples = [
    {"text": "如何烹饪红烧肉", "label": "食谱"},
    {"text": "如何制作咖啡", "label": "饮品"},
    {"text": "如何修理自行车", "label": "维修"},
]

selector = FewShotSelector(examples)
best = selector.select_best_examples("怎么做可乐鸡翅", k=2)

# 估算 Token 节省
savings = selector.estimate_token_savings("怎么做可乐鸡翅", k=2)
print(f"Token 节省: {savings['savings_percent']:.1f}%")
```

**效果**：平均 Token 节省 30-60%

### 7. 响应字段过滤

只提取需要的字段，减少返回的 tokens。

```python
from advanced_strategies import ResponseFilter

original = {
    "status": "success",
    "message": "操作成功",
    "data": {"user_id": 12345, "user_name": "张三", "email": "zhangsan@example.com"}
}

# 只提取需要的字段
filtered = ResponseFilter.filter(original, ["status", "data.user_name"])

# 估算节省
savings = ResponseFilter.estimate_token_savings(original, filtered)
print(f"Token 节省: {savings['savings_percent']:.1f}%")
```

**效果**：Token 节省高达 70%+

### 8. Token 成本估算

精确计算 API 调用成本，支持缓存折扣。

```python
from advanced_strategies import CostEstimator, TokenCost

# 估算单次成本
cost = CostEstimator.estimate_cost(
    prompt_tokens=1000,
    completion_tokens=500,
    cached_tokens=400,  # 缓存的 tokens
    model="gpt-4"
)

print(f"Prompt tokens: {cost.prompt_tokens}")
print(f"Completion tokens: {cost.completion_tokens}")
print(f"Cached tokens: {cost.cached_tokens}")
```

### 9. 结构化输出优化

优化 JSON 输出结构，缩短字段名减少 token。

```python
from advanced_strategies import StructuredOutputOptimizer

data = {
    "status": "success",
    "message": "操作成功完成",
    "data": {"user_id": 123, "name": "张三"}
}

# 优化字段名
optimized = StructuredOutputOptimizer.optimize(data)
# {'s': 'success', 'm': '操作成功完成', 'd': {'user_id': 123, 'name': '张三'}}
```

**效果**：Token 节省 15-30%

### 10. 上下文压缩

用于 RAG 场景，将长文本压缩为关键信息。

```python
from advanced_strategies import ContextCompressor

compressor = ContextCompressor(max_length=200)

# 压缩长文本
compressed = compressor.compress(long_text)

# 提取关键点
key_points = compressor.extract_key_points(long_text)
```

### 11. LLM Cascade（模型级联）

动态选择最优模型，简单问题用小模型，复杂问题用大模型。

```python
from advanced_strategies import LLMCascade

cascade = LLMCascade()

# 根据复杂度选择模型
simple_model = cascade.select_model(0.3)   # 简单问题 -> gpt-3.5-turbo
complex_model = cascade.select_model(0.8)  # 复杂问题 -> gpt-4-turbo

# 估算成本差异
diff = cascade.estimate_cost_difference("问题", "gpt-3.5-turbo", "gpt-4")
print(f"节省: {diff['savings_percent']:.1f}%")
```

## 决策树

```
需要优化API调用?
│
├── 是否需要减少请求次数?
│   ├── 是 ──▶ 考虑GraphQL批量查询
│   └── 否 ──▶ 继续
│
├── 是否需要缓存响应?
│   ├── 是 ──▶ LRU + TTL缓存 + Prompt Caching
│   └── 否 ──▶ 继续
│
├── 是否有多个Token/账号?
│   ├── 是 ──▶ Token池 + 轮询策略
│   └── 否 ──▶ 继续
│
├── 是否经常轮询?
│   ├── 是 ──▶ Webhook替代 + 增量获取
│   └── 否 ──▶ 继续
│
├── 是否需要精选示例?
│   ├── 是 ──▶ Few-shot语义相似度选择
│   └── 否 ──▶ 继续
│
├── 是否需要过滤响应?
│   ├── 是 ──▶ 字段过滤 + 结构化输出
│   └── 否 ──▶ 继续
│
└── 需要容错机制?
    ├── 是 ──▶ 熔断 + 优雅降级
    └── 否 ──▶ 完成
```

## 配置文件模板

### GitHub API 配置
```yaml
# config/github.yaml
github:
  tokens:
    - $GITHUB_TOKEN_1
    - $GITHUB_TOKEN_2
  rate_limit: 5000  # per hour
  cache:
    enabled: true
    ttl: 3600  # 1 hour
  retry:
    max_attempts: 3
    backoff: exponential
```

### OpenAI API 配置
```yaml
# config/openai.yaml
openai:
  api_key: $OPENAI_API_KEY
  organization: $ORG_ID
  cache:
    enabled: true
    ttl: 86400  # 24 hours for embeddings
  prompt:
    compress: true  # 启用prompt压缩
    few_shot_selection: true  # 启用few-shot精选
  fallback:
    enabled: true
    cached_responses: ./cache/responses.json
  advanced:
    prompt_caching: true
    field_filtering: true
    structured_output: true
```

## 优化效果对比

| 优化策略 | Token节省 | 延迟降低 | 成本降低 |
|---------|----------|---------|---------|
| LRU缓存 | 30-70% | 50-90% | 30-70% |
| Prompt Caching | 80-90% | 80% | 80% |
| Few-shot精选 | 30-60% | 20-40% | 30-60% |
| 字段过滤 | 50-80% | 10-20% | 50-80% |
| 结构化输出 | 15-30% | 5-15% | 15-30% |
| LLM Cascade | 50-90% | 30-60% | 50-90% |

## 触发条件

### 核心触发词（100%覆盖）
- API、token、quota、配额、限制、限流、rate limit、429、quota exceeded
- 缓存、cache、caching、复用、reuse、减少请求、reduce requests
- 优化、optimize、节省、save、降低、reduce、成本、cost、费用、expense
- 调用、call、request、invoke、API调用、接口调用
- 轮询、poll、轮询策略、token池、token pool、多token
- 熔断、circuit breaker、降级、degradation、fallback、兜底
- Prompt、提示、few-shot、示例、example、上下文、context
- 字段过滤、filter、结构化输出、structured output、压缩、compress

### 场景触发词
- 如何节省API费用、如何减少token消耗、如何优化API调用
- API调用太慢、API调用失败、API超时、API限流
- 需要缓存API响应、需要实现限流、需要Token轮询
- 计算API成本、估算token费用、统计API调用次数
- Prompt太长、需要压缩prompt、需要few-shot示例
- 需要降级方案、需要容错机制、需要熔断保护

### 技术触发词
- GitHub API、OpenAI API、AWS API、REST API、GraphQL
- gpt-4、gpt-3.5、claude、LLM、大模型
- embedding、向量、embedding API
- webhook、webhook替代、增量获取、incremental fetch

---

**版本**: v2.0 | **日期**: 2026-05-15 | **新增**: Prompt Caching, Few-shot精选, 字段过滤, 成本估算, 结构化输出, 上下文压缩, LLM Cascade