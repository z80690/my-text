"""
API Token Optimizer 高级策略
新增功能：
1. Prompt Caching（提示缓存）
2. Few-shot 精选示例
3. 响应字段过滤
4. Token 成本估算
5. 结构化输出约束
6. 上下文压缩
7. LLM Cascade
"""

import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable, Union
from dataclasses import dataclass


# ================================================
# 1. Prompt Caching（提示缓存）
# ================================================
class PromptCache:
    """
    OpenAI 风格的提示缓存
    缓存超过 1024 tokens 的提示，节省高达 80% 成本
    """

    def __init__(self, cache_threshold: int = 1024, ttl_seconds: int = 3600):
        self.cache_threshold = cache_threshold
        self.ttl = ttl_seconds
        self.cache: Dict[str, Dict] = {}
        self.hit_count = 0
        self.miss_count = 0

    def _estimate_tokens(self, text: str) -> int:
        """估算 token 数量（简单估算：中文约2字符=1 token，英文约4字符=1 token）"""
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return int(chinese_chars / 2 + other_chars / 4)

    def _make_key(self, prompt: str, model: str = "gpt-4") -> str:
        """生成缓存 key"""
        content = json.dumps({"prompt": prompt, "model": model}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, prompt: str, model: str = "gpt-4") -> Optional[Dict]:
        """获取缓存的响应"""
        key = self._make_key(prompt, model)
        if key not in self.cache:
            self.miss_count += 1
            return None

        entry = self.cache[key]
        if time.time() - entry["timestamp"] > self.ttl:
            del self.cache[key]
            self.miss_count += 1
            return None

        entry["hits"] += 1
        self.hit_count += 1
        return entry["response"]

    def set(self, prompt: str, response: Any, model: str = "gpt-4"):
        """缓存响应"""
        key = self._make_key(prompt, model)
        tokens = self._estimate_tokens(prompt)

        self.cache[key] = {
            "response": response,
            "timestamp": time.time(),
            "hits": 0,
            "prompt_tokens": tokens,
            "cached": tokens >= self.cache_threshold
        }

    def get_stats(self) -> Dict:
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        cached_entries = sum(1 for e in self.cache.values() if e.get("cached"))

        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "cached_entries": cached_entries,
            "total_entries": len(self.cache)
        }


# ================================================
# 2. Few-shot 精选示例
# ================================================
class FewShotSelector:
    """
    语义相似度选择最相关的 Few-shot 示例
    减少 token 消耗同时保持准确性
    """

    def __init__(self, examples: List[Dict], embedding_func: Callable = None):
        self.examples = examples
        self.embedding_func = embedding_func or self._simple_embedding
        self.example_embeddings = [self._simple_embedding(e.get("text", str(e))) for e in examples]

    def _simple_embedding(self, text: str) -> List[float]:
        """简单的文本嵌入（基于词频）"""
        words = text.lower().split()
        embedding = [0.0] * 128

        for i, word in enumerate(words[:128]):
            embedding[i % 128] += hash(word) % 100 / 100.0

        norm = sum(e * e for e in embedding) ** 0.5
        return [e / norm if norm > 0 else 0 for e in embedding]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """计算余弦相似度"""
        return sum(x * y for x, y in zip(a, b))

    def select_best_examples(self, query: str, k: int = 3) -> List[Dict]:
        """选择与查询最相关的 k 个示例"""
        query_embedding = self._simple_embedding(query)
        similarities = [
            (i, self._cosine_similarity(query_embedding, emb))
            for i, emb in enumerate(self.example_embeddings)
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_k_indices = [i for i, _ in similarities[:k]]

        return [self.examples[i] for i in top_k_indices]

    def estimate_token_savings(self, query: str, k: int = 3) -> Dict:
        """估算 token 节省"""
        all_examples_text = "\n".join(str(e) for e in self.examples)
        selected_examples = self.select_best_examples(query, k)
        selected_text = "\n".join(str(e) for e in selected_examples)

        def estimate_tokens(text: str) -> int:
            chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            return int(chinese / 2 + (len(text) - chinese) / 4)

        all_tokens = estimate_tokens(all_examples_text)
        selected_tokens = estimate_tokens(selected_text)

        return {
            "all_examples_tokens": all_tokens,
            "selected_tokens": selected_tokens,
            "savings": all_tokens - selected_tokens,
            "savings_percent": ((all_tokens - selected_tokens) / all_tokens * 100) if all_tokens > 0 else 0
        }


# ================================================
# 3. 响应字段过滤
# ================================================
class ResponseFilter:
    """
    只提取响应中需要的字段，减少输出 token
    """

    @staticmethod
    def filter(data: Dict, fields: List[str]) -> Dict:
        """从响应中提取指定字段"""
        if not fields:
            return data

        result = {}
        for field in fields:
            if "." in field:
                parts = field.split(".")
                current = data
                for part in parts:
                    if isinstance(current, dict):
                        current = current.get(part)
                    else:
                        current = None
                        break
                result[field.replace(".", "_")] = current
            else:
                result[field] = data.get(field)

        return result

    @staticmethod
    def flatten(data: Any, prefix: str = "") -> Dict:
        """扁平化嵌套数据"""
        result = {}

        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    result.update(ResponseFilter.flatten(value, new_key))
                else:
                    result[new_key] = value
        elif isinstance(data, list):
            for i, item in enumerate(data):
                result.update(ResponseFilter.flatten(item, f"{prefix}[{i}]"))

        return result

    @staticmethod
    def estimate_token_savings(original: Dict, filtered: Dict) -> Dict:
        """估算过滤后的 token 节省"""
        original_str = json.dumps(original, ensure_ascii=False)
        filtered_str = json.dumps(filtered, ensure_ascii=False)

        def estimate_tokens(text: str) -> int:
            chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            return int(chinese / 2 + (len(text) - chinese) / 4)

        original_tokens = estimate_tokens(original_str)
        filtered_tokens = estimate_tokens(filtered_str)

        return {
            "original_tokens": original_tokens,
            "filtered_tokens": filtered_tokens,
            "savings": original_tokens - filtered_tokens,
            "savings_percent": ((original_tokens - filtered_tokens) / original_tokens * 100) if original_tokens > 0 else 0
        }


# ================================================
# 4. Token 成本估算
# ================================================
@dataclass
class TokenCost:
    prompt_tokens: int
    completion_tokens: int
    cached_tokens: int = 0


class CostEstimator:
    """
    精确计算 API 调用成本
    支持多种模型和缓存折扣
    """

    # OpenAI 定价（每 1M tokens）
    PRICING = {
        "gpt-4": {"prompt": 30.0, "completion": 60.0},
        "gpt-4-turbo": {"prompt": 10.0, "completion": 30.0},
        "gpt-3.5-turbo": {"prompt": 0.5, "completion": 1.5},
        "gpt-3.5-turbo-16k": {"prompt": 1.0, "completion": 2.0},
        "claude-3-opus": {"prompt": 15.0, "completion": 75.0},
        "claude-3-sonnet": {"prompt": 3.0, "completion": 15.0},
    }

    # 缓存折扣（OpenAI Prompt Caching）
    CACHE_DISCOUNT = 0.5  # 缓存提示50%折扣

    @classmethod
    def estimate_cost(
        cls,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "gpt-4",
        cached_tokens: int = 0
    ) -> TokenCost:
        """估算单次调用成本"""
        pricing = cls.PRICING.get(model, cls.PRICING["gpt-4"])

        prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]

        if cached_tokens > 0:
            cached_prompt_cost = (cached_tokens / 1_000_000) * pricing["prompt"] * cls.CACHE_DISCOUNT
            uncached_prompt_tokens = prompt_tokens - cached_tokens
            uncached_prompt_cost = (uncached_prompt_tokens / 1_000_000) * pricing["prompt"]
            prompt_cost = cached_prompt_cost + uncached_prompt_cost

        return TokenCost(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cached_tokens=cached_tokens
        )

    @classmethod
    def calculate_total_cost(cls, costs: List[TokenCost], model: str = "gpt-4") -> float:
        """计算总成本"""
        pricing = cls.PRICING.get(model, cls.PRICING["gpt-4"])
        total = 0.0

        for cost in costs:
            prompt_cost = (cost.prompt_tokens / 1_000_000) * pricing["prompt"]
            completion_cost = (cost.completion_tokens / 1_000_000) * pricing["completion"]

            if cost.cached_tokens > 0:
                cached_prompt_cost = (cost.cached_tokens / 1_000_000) * pricing["prompt"] * cls.CACHE_DISCOUNT
                uncached_tokens = cost.prompt_tokens - cost.cached_tokens
                uncached_cost = (uncached_tokens / 1_000_000) * pricing["prompt"]
                prompt_cost = cached_prompt_cost + uncached_cost

            total += prompt_cost + completion_cost

        return total

    @classmethod
    def estimate_savings(cls, original_cost: float, optimized_cost: float) -> Dict:
        """估算节省"""
        savings = original_cost - optimized_cost
        savings_percent = (savings / original_cost * 100) if original_cost > 0 else 0

        return {
            "original_cost": original_cost,
            "optimized_cost": optimized_cost,
            "savings": savings,
            "savings_percent": savings_percent
        }


# ================================================
# 5. 结构化输出约束
# ================================================
class StructuredOutputOptimizer:
    """
    优化 JSON 输出，减少 token 消耗
    - 缩短字段名
    - 移除冗余数据
    - 约束输出格式
    """

    # 字段名映射（长 -> 短）
    FIELD_MAPPING = {
        "status": "s",
        "message": "m",
        "data": "d",
        "result": "r",
        "error": "e",
        "timestamp": "t",
        "response": "resp",
        "content": "c",
        "description": "desc",
        "information": "info",
        "successfully": "ok",
        "parameters": "params",
        "configuration": "cfg",
    }

    @classmethod
    def optimize(cls, data: Any, minify: bool = False) -> Any:
        """优化 JSON 结构"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                new_key = cls.FIELD_MAPPING.get(key, key)
                result[new_key] = cls.optimize(value, minify)
            return result if not minify else json.dumps(result, separators=(',', ':'))
        elif isinstance(data, list):
            return [cls.optimize(item, minify) for item in data]
        else:
            return data

    @classmethod
    def estimate_savings(cls, original: Any, optimized: Any) -> Dict:
        """估算优化后的 token 节省"""
        original_str = json.dumps(original, ensure_ascii=False)
        optimized_str = json.dumps(optimized, ensure_ascii=False)

        def estimate_tokens(text: str) -> int:
            chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            return int(chinese / 2 + (len(text) - chinese) / 4)

        original_tokens = estimate_tokens(original_str)
        optimized_tokens = estimate_tokens(optimized_str)

        return {
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "savings": original_tokens - optimized_tokens,
            "savings_percent": ((original_tokens - optimized_tokens) / original_tokens * 100) if original_tokens > 0 else 0
        }


# ================================================
# 6. 上下文压缩
# ================================================
class ContextCompressor:
    """
    上下文压缩，用于 RAG 场景
    将长文本压缩为关键信息，减少 token 消耗
    """

    def __init__(self, max_length: int = 500):
        self.max_length = max_length

    def compress(self, text: str, preserve_keywords: List[str] = None) -> str:
        """压缩文本，保留关键信息"""
        if preserve_keywords is None:
            preserve_keywords = []

        sentences = text.replace("!", ".").replace("?", ".").split(".")
        sentences = [s.strip() for s in sentences if s.strip()]

        important_sentences = []
        total_length = 0

        for sentence in sentences:
            sentence_len = len(sentence)
            if total_length + sentence_len <= self.max_length:
                important_sentences.append(sentence)
                total_length += sentence_len
            else:
                if important_sentences:
                    break

        result = ". ".join(important_sentences)
        if result and not result.endswith("."):
            result += "."

        return result

    def extract_key_points(self, text: str) -> List[str]:
        """提取关键点"""
        sentences = text.replace("!", ".").replace("?", ".").split(".")
        sentences = [s.strip() for s in sentences if s.strip()]

        key_points = []
        for sentence in sentences[:5]:
            if any(kw in sentence.lower() for kw in ["important", "key", "main", "critical", "essential"]):
                key_points.append(sentence)

        if not key_points:
            key_points = sentences[:3]

        return key_points


# ================================================
# 7. LLM Cascade（模型级联）
# ================================================
class LLMCascade:
    """
    动态选择最优模型
    简单问题用小模型，复杂问题用大模型
    """

    def __init__(self, models: List[Dict] = None):
        self.models = models or [
            {"name": "gpt-3.5-turbo", "cost": 0.002, "capability": 0.7},
            {"name": "gpt-4", "cost": 0.06, "capability": 0.9},
            {"name": "gpt-4-turbo", "cost": 0.03, "capability": 0.95},
        ]

    def select_model(self, query_complexity: float = 0.5) -> Dict:
        """
        根据查询复杂度选择模型
        complexity: 0.0-1.0，0表示简单，1表示复杂
        """
        for model in self.models:
            if model["capability"] >= query_complexity:
                return model

        return self.models[-1]

    def estimate_cost_difference(self, query: str, model_a: str, model_b: str) -> Dict:
        """估算两个模型的成本差异"""
        def estimate_tokens(text: str) -> int:
            chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            return int(chinese / 2 + (len(text) - chinese) / 4)

        tokens = estimate_tokens(query)

        model_a_info = next((m for m in self.models if m["name"] == model_a), self.models[0])
        model_b_info = next((m for m in self.models if m["name"] == model_b), self.models[1])

        cost_a = (tokens / 1_000_000) * model_a_info["cost"] * 2
        cost_b = (tokens / 1_000_000) * model_b_info["cost"] * 2

        return {
            "model_a": model_a,
            "model_b": model_b,
            "cost_a": cost_a,
            "cost_b": cost_b,
            "savings": cost_b - cost_a,
            "savings_percent": ((cost_b - cost_a) / cost_b * 100) if cost_b > 0 else 0
        }


# ================================================
# 综合优化器
# ================================================
class ComprehensiveOptimizer:
    """
    综合优化器 - 整合所有优化策略
    """

    def __init__(self):
        self.prompt_cache = PromptCache()
        self.cost_estimator = CostEstimator()
        self.response_filter = ResponseFilter()
        self.structured_optimizer = StructuredOutputOptimizer()
        self.context_compressor = ContextCompressor()
        self.llm_cascade = LLMCascade()

    def optimize_request(
        self,
        prompt: str,
        use_cache: bool = True,
        use_few_shot: bool = False,
        few_shot_examples: List[Dict] = None,
        filter_fields: List[str] = None,
        model: str = "gpt-4"
    ) -> Dict:
        """综合优化请求"""
        result = {
            "original_prompt": prompt,
            "optimized_prompt": prompt,
            "cache_hit": False,
            "estimated_tokens": 0,
            "estimated_cost": 0.0,
            "optimizations_applied": []
        }

        # 1. Prompt Caching
        if use_cache:
            cached_response = self.prompt_cache.get(prompt, model)
            if cached_response:
                result["cache_hit"] = True
                result["optimizations_applied"].append("prompt_cache")
                return {**result, "response": cached_response}

        # 2. Few-shot 精选
        if use_few_shot and few_shot_examples:
            selector = FewShotSelector(few_shot_examples)
            best_examples = selector.select_best_examples(prompt, k=3)
            savings = selector.estimate_token_savings(prompt, k=3)
            result["optimizations_applied"].append("few_shot_selection")
            result["few_shot_savings"] = savings

        # 3. Token 估算
        def estimate_tokens(text: str) -> int:
            chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            return int(chinese / 2 + (len(text) - chinese) / 4)

        result["estimated_tokens"] = estimate_tokens(prompt)
        result["estimated_cost"] = self.cost_estimator.estimate_cost(
            result["estimated_tokens"],
            completion_tokens=100,
            model=model
        )

        return result

    def optimize_response(
        self,
        response: Dict,
        filter_fields: List[str] = None,
        use_structured_output: bool = False
    ) -> Dict:
        """综合优化响应"""
        result = {
            "original_response": response,
            "optimized_response": response,
            "optimizations_applied": []
        }

        # 1. 字段过滤
        if filter_fields:
            filtered = self.response_filter.filter(response, filter_fields)
            savings = self.response_filter.estimate_token_savings(response, filtered)
            result["optimized_response"] = filtered
            result["optimizations_applied"].append("field_filtering")
            result["filter_savings"] = savings

        # 2. 结构化输出优化
        if use_structured_output:
            optimized = self.structured_optimizer.optimize(result["optimized_response"])
            savings = self.structured_optimizer.estimate_savings(
                result["optimized_response"],
                optimized
            )
            result["optimized_response"] = optimized
            result["optimizations_applied"].append("structured_output")
            result["structured_savings"] = savings

        return result

    def get_all_stats(self) -> Dict:
        """获取所有优化统计"""
        return {
            "prompt_cache": self.prompt_cache.get_stats(),
            "llm_cascade_models": [m["name"] for m in self.llm_cascade.models]
        }


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 API Token Optimizer 高级策略测试")
    print("=" * 60)

    # 测试 1: Prompt Caching
    print("\n📦 测试 1: Prompt Caching")
    cache = PromptCache()
    test_prompt = "这是一段很长的提示文本，用于测试缓存功能。" * 100
    cache.set(test_prompt, {"result": "success"})
    result = cache.get(test_prompt)
    print(f"  缓存命中: {result is not None}")
    print(f"  统计: {cache.get_stats()}")

    # 测试 2: Few-shot 精选
    print("\n🎯 测试 2: Few-shot 精选")
    examples = [
        {"text": "如何烹饪红烧肉", "label": "食谱"},
        {"text": "如何制作咖啡", "label": "饮品"},
        {"text": "如何修理自行车", "label": "维修"},
        {"text": "如何煮米饭", "label": "食谱"},
        {"text": "如何冲泡茶", "label": "饮品"},
    ]
    selector = FewShotSelector(examples)
    query = "怎么做可乐鸡翅"
    best = selector.select_best_examples(query, k=2)
    savings = selector.estimate_token_savings(query, k=2)
    print(f"  查询: {query}")
    print(f"  选中示例: {[e['label'] for e in best]}")
    print(f"  Token 节省: {savings['savings']} ({savings['savings_percent']:.1f}%)")

    # 测试 3: 响应字段过滤
    print("\n🔍 测试 3: 响应字段过滤")
    original = {
        "status": "success",
        "message": "操作成功",
        "data": {
            "user_id": 12345,
            "user_name": "张三",
            "email": "zhangsan@example.com",
            "created_at": "2024-01-01 00:00:00"
        }
    }
    filtered = ResponseFilter.filter(original, ["status", "data.user_name"])
    savings = ResponseFilter.estimate_token_savings(original, filtered)
    print(f"  原响应: {original}")
    print(f"  过滤后: {filtered}")
    print(f"  Token 节省: {savings['savings']} ({savings['savings_percent']:.1f}%)")

    # 测试 4: Token 成本估算
    print("\n💰 测试 4: Token 成本估算")
    cost = CostEstimator.estimate_cost(
        prompt_tokens=1000,
        completion_tokens=500,
        cached_tokens=400,
        model="gpt-4"
    )
    print(f"  Prompt tokens: {cost.prompt_tokens}")
    print(f"  Completion tokens: {cost.completion_tokens}")
    print(f"  Cached tokens: {cost.cached_tokens}")

    # 测试 5: 结构化输出优化
    print("\n📋 测试 5: 结构化输出优化")
    data = {
        "status": "success",
        "message": "操作成功完成",
        "data": {"user_id": 123, "name": "张三"}
    }
    optimized = StructuredOutputOptimizer.optimize(data)
    print(f"  优化前: {data}")
    print(f"  优化后: {optimized}")

    # 测试 6: 上下文压缩
    print("\n📝 测试 6: 上下文压缩")
    compressor = ContextCompressor(max_length=100)
    long_text = "这是一个很长的文本。它包含很多句子。有些是重要的。关键点在这里。还有一些其他信息。最后一个句子。"
    compressed = compressor.compress(long_text)
    print(f"  压缩前: {long_text}")
    print(f"  压缩后: {compressed}")

    # 测试 7: LLM Cascade
    print("\n🤖 测试 7: LLM Cascade")
    cascade = LLMCascade()
    simple_model = cascade.select_model(0.3)
    complex_model = cascade.select_model(0.8)
    print(f"  简单问题 -> 模型: {simple_model['name']}")
    print(f"  复杂问题 -> 模型: {complex_model['name']}")

    print("\n" + "=" * 60)
    print("✅ 所有高级策略测试完成!")
    print("=" * 60)