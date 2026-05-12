"""
API Token Optimizer - 代码示例
包含多Token轮询、LRU缓存、条件请求等核心实现
"""

import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from functools import lru_cache
import requests


class TokenPool:
    """多Token池管理器"""

    def __init__(self, tokens: List[Dict[str, Any]]):
        self.tokens = tokens
        self.current_index = 0

    def get_token(self) -> Optional[Dict[str, Any]]:
        """获取当前可用的token"""
        if not self.tokens:
            return None

        attempts = 0
        while attempts < len(self.tokens):
            token_info = self.tokens[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.tokens)

            if token_info.get("remaining", 0) > 0:
                if token_info.get("reset_at", 0) <= time.time():
                    return token_info
            attempts += 1

        return None

    def update_token_usage(self, token: str, remaining: int, reset_at: int):
        """更新token使用情况"""
        for t in self.tokens:
            if t["token"] == token:
                t["remaining"] = remaining
                t["reset_at"] = reset_at
                break


class CircuitBreaker:
    """熔断器 - 防止级联故障"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 30):
        self.state = "CLOSED"
        self.failure_count = 0
        self.success_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True

    def record_success(self):
        self.success_count += 1
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class LRUCache:
    """带TTL的LRU缓存"""

    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl_seconds

    def _make_key(self, *args, **kwargs) -> str:
        """生成缓存key"""
        key_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _is_expired(self, timestamp: float) -> bool:
        return (datetime.now() - datetime.fromtimestamp(timestamp)).total_seconds() > self.ttl

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            if not self._is_expired(entry["timestamp"]):
                entry["hits"] = entry.get("hits", 0) + 1
                return entry["value"]
            del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]

        self.cache[key] = {
            "value": value,
            "timestamp": datetime.now().timestamp(),
            "hits": 0
        }

    def clear(self):
        self.cache.clear()


class APIClient:
    """API客户端 - 集成缓存、熔断、Token轮询"""

    def __init__(self, base_url: str, tokens: List[str]):
        self.base_url = base_url
        self.token_pool = TokenPool([
            {"token": t, "remaining": 5000, "reset_at": 0} for t in tokens
        ])
        self.circuit_breaker = CircuitBreaker()
        self.cache = LRUCache(max_size=100, ttl_seconds=300)

    def request(self, method: str, endpoint: str, use_cache: bool = True, **kwargs) -> Dict:
        """发起API请求"""
        if not self.circuit_breaker.can_execute():
            cached = self.cache.get(endpoint)
            if cached:
                return {"source": "cache", "data": cached}
            raise Exception("Circuit breaker is OPEN")

        cache_key = self._make_cache_key(endpoint, kwargs)

        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return {"source": "cache", "data": cached}

        token_info = self.token_pool.get_token()
        if not token_info:
            raise Exception("No available tokens")

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token_info['token']}"

        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, headers=headers, **kwargs)

        if response.status_code == 200:
            self.circuit_breaker.record_success()
            data = response.json()

            if "X-RateLimit-Remaining" in response.headers:
                self.token_pool.update_token_usage(
                    token_info["token"],
                    int(response.headers["X-RateLimit-Remaining"]),
                    int(response.headers["X-RateLimit-Reset"])
                )

            if use_cache:
                self.cache.set(cache_key, data)

            return {"source": "api", "data": data}

        elif response.status_code == 429:
            self.circuit_breaker.record_failure()
            raise Exception("Rate limit exceeded")

        else:
            self.circuit_breaker.record_failure()
            raise Exception(f"API error: {response.status_code}")

    def _make_cache_key(self, endpoint: str, params: dict) -> str:
        return hashlib.md5(f"{endpoint}:{json.dumps(params, sort_keys=True)}".encode()).hexdigest()


def conditional_request(url: str, etag: str = None) -> Dict[str, Any]:
    """条件请求 - 利用HTTP ETag"""
    headers = {}
    if etag:
        headers["If-None-Match"] = etag

    response = requests.get(url, headers=headers)

    if response.status_code == 304:
        return {"cached": True, "etag": etag}

    new_etag = response.headers.get("ETag")
    return {
        "cached": False,
        "data": response.json() if response.content else None,
        "etag": new_etag,
        "status": response.status_code
    }


def incremental_fetch(
    fetch_func: Callable,
    params: Dict[str, Any],
    id_field: str = "id",
    per_page: int = 100
) -> List[Dict]:
    """增量获取数据"""
    all_items = []
    last_id = None

    while True:
        query_params = {**params, "per_page": per_page}
        if last_id:
            query_params["since_id"] = last_id

        response = fetch_func(**query_params)
        items = response.get("items", [])

        if not items:
            break

        all_items.extend(items)
        last_id = items[-1].get(id_field)

        if len(items) < per_page:
            break

    return all_items


if __name__ == "__main__":
    print("API Token Optimizer - 代码示例")
    print("=" * 50)

    cache = LRUCache(max_size=3, ttl_seconds=60)
    cache.set("key1", {"data": "value1"})
    cache.set("key2", {"data": "value2"})
    cache.set("key3", {"data": "value3"})

    print(f"Cache size: {len(cache.cache)}")

    result = cache.get("key1")
    print(f"Get key1: {result}")

    breaker = CircuitBreaker(failure_threshold=3, timeout=5)
    print(f"Circuit breaker state: {breaker.state}")

    print("\n代码示例运行成功!")
