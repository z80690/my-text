---
name: "api-token-optimizer"
description: "API Token优化技能，涵盖缓存、限流、轮询、优雅降级等策略。Invoke when user needs to optimize API calls, reduce token consumption, or implement rate limiting."
---

# API Token Optimizer

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

#### REST vs GraphQL 请求合并
```graphql
# GraphQL批量查询示例 - 一次请求获取多个资源
query {
  user(id: "123") {
    name
    email
  }
  repositories(first: 10) {
    nodes {
      name
      url
      stars
    }
  }
  rateLimit {
    limit
    remaining
  }
}
```

```python
# REST对比 - 需要多次请求
# GET /users/123
# GET /users/123/repos
# 每个请求都消耗token
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
    
    # 处理不同事件
    if event == 'push':
        handle_push(data)
    elif event == 'pull_request':
        handle_pr(data)
    
    return jsonify({"status": "ok"})

def handle_push(data):
    # 仅在有实际更新时处理
    print(f"Received push to {data.get('repository')}")
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
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │  Cache  │    │  Rate   │    │  Token  │    │Fallback │  │
│  │  Layer  │───▶│  Limit  │───▶│  Router │───▶│  Layer  │  │
│  │ (LRU+TTLv)    │(Token Bucket)  │(Pool)   │    │(Cached) │  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
│       │              │              │              │         │
│       └──────────────┴──────────────┴──────────────┘         │
│                          │                                    │
│                    ┌─────▼─────┐                             │
│                    │ Monitoring │                             │
│                    │ & Metrics  │                             │
│                    └───────────┘                             │
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
        # 1. 尝试从缓存获取
        cached = self.cache.get(key)
        if cached:
            return {"source": "cache", "data": cached}
        
        # 2. 尝试调用API
        try:
            data = primary_func()
            self.cache.set(key, data)
            return {"source": "api", "data": data}
        except APIError as e:
            # 3. API失败，返回兜底数据
            if fallback_data:
                return {"source": "fallback", "data": fallback_data}
            raise e
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
│   ├── 是 ──▶ LRU + TTL缓存
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
  fallback:
    enabled: true
    cached_responses: ./cache/responses.json
```

## RTK项目核心思想借鉴

RTK (Rust Token Killer) 的优化哲学：

| RTK技术 | API优化应用 |
|---------|------------|
| 命令输出过滤 | Response过滤，只提取关键字段 |
| 智能截断 | 大响应分页+游标 |
| 重复内容折叠 | Delta更新+变化检测 |
| 上下文压缩 | Prompt精简+结构化输出 |

## 性能对比基准测试

```python
def benchmark_optimization():
    """
    量化展示优化效果
    """
    results = {
        "no_optimization": {
            "requests": 100,
            "tokens": 50000,
            "cost": 0.50
        },
        "with_cache": {
            "requests": 30,
            "tokens": 15000,
            "cost": 0.15,
            "savings": "70%"
        },
        "with_all": {
            "requests": 10,
            "tokens": 5000,
            "cost": 0.05,
            "savings": "90%"
        }
    }
    return results
```

## 触发条件

- 用户询问如何节省API Token
- 需要实现限流或缓存机制
- 遇到API rate limit问题
- 需要优化API调用性能
- 请求架构设计或降级策略
