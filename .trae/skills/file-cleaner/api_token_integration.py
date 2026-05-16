# -*- coding: utf-8 -*-
"""
API Token Optimizer v2.0 集成到 File Cleaner
功能：
1. 清理 API 缓存文件
2. 优化 Token 使用报告
3. 检测浪费的 API 调用
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class APITokenOptimizerIntegration:
    """
    集成 API Token Optimizer v2.0 到文件清理技能
    """
    
    def __init__(self):
        self.api_cache_patterns = [
            "*.cache",
            ".api_cache/",
            "token_cache/",
            "cache/",
            "*.token",
            ".cache/",
            "api_token_cache/",
            "prompt_cache/",
        ]
    
    def scan_api_cache(self, directory: str) -> Dict[str, Any]:
        """扫描 API 缓存和 Token 相关文件"""
        result = {
            "api_cache_files": [],
            "token_files": [],
            "total_size": 0,
            "optimizable": []
        }
        
        dir_path = Path(directory)
        for pattern in self.api_cache_patterns:
            if pattern.endswith('/'):
                # 目录模式
                for path in dir_path.rglob(pattern.rstrip('/')):
                    if path.is_dir():
                        size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                        result["api_cache_files"].append({
                            "path": str(path),
                            "size": size,
                            "type": "directory"
                        })
                        result["total_size"] += size
            else:
                # 文件模式
                for path in dir_path.rglob(pattern):
                    if path.is_file():
                        result["api_cache_files"].append({
                            "path": str(path),
                            "size": path.stat().st_size,
                            "type": "file"
                        })
                        result["total_size"] += path.stat().st_size
        
        return result
    
    def get_optimization_report(self, directory: str) -> Dict[str, Any]:
        """获取 API Token 优化报告"""
        cache_info = self.scan_api_cache(directory)
        
        report = {
            "total_cache_size": cache_info["total_size"],
            "cache_file_count": len(cache_info["api_cache_files"]),
            "recommendations": [],
            "estimated_savings": {
                "storage_bytes": cache_info["total_size"],
                "api_calls_reduced": 0,
                "token_savings_percent": 0
            }
        }
        
        # 生成优化建议
        if cache_info["total_size"] > 10 * 1024 * 1024:  # > 10MB
            report["recommendations"].append({
                "type": "cache_cleanup",
                "priority": "high",
                "description": "API 缓存过大，建议清理",
                "estimated_savings": f"{cache_info['total_size'] / 1024 / 1024:.2f}MB"
            })
        
        if len(cache_info["api_cache_files"]) > 100:
            report["recommendations"].append({
                "type": "cache_consolidation",
                "priority": "medium",
                "description": "缓存文件过多，建议合并或清理",
                "estimated_savings": f"{len(cache_info['api_cache_files'])} 个文件"
            })
        
        return report
    
    def clean_api_cache(self, directory: str, dry_run: bool = True) -> Dict[str, Any]:
        """清理 API 缓存"""
        cache_info = self.scan_api_cache(directory)
        result = {
            "deleted_files": [],
            "deleted_dirs": [],
            "total_size_freed": 0,
            "dry_run": dry_run
        }
        
        for item in cache_info["api_cache_files"]:
            path = Path(item["path"])
            
            if dry_run:
                result["deleted_files" if item["type"] == "file" else "deleted_dirs"].append({
                    "path": item["path"],
                    "size": item["size"]
                })
                result["total_size_freed"] += item["size"]
            else:
                try:
                    if item["type"] == "file":
                        path.unlink()
                    else:
                        import shutil
                        shutil.rmtree(path)
                    
                    result["deleted_files" if item["type"] == "file" else "deleted_dirs"].append({
                        "path": item["path"],
                        "size": item["size"]
                    })
                    result["total_size_freed"] += item["size"]
                except Exception as e:
                    result.setdefault("errors", []).append({
                        "path": item["path"],
                        "error": str(e)
                    })
        
        return result
    
    def get_token_usage_report(self, directory: str) -> Dict[str, Any]:
        """获取 Token 使用报告（分析 API 调用日志）"""
        report = {
            "total_api_calls": 0,
            "cached_calls": 0,
            "uncached_calls": 0,
            "estimated_tokens_saved": 0,
            "optimization_suggestions": []
        }
        
        # 查找 API 调用日志
        log_patterns = ["*.log", "api_calls.json", "token_usage.json"]
        for pattern in log_patterns:
            for log_file in Path(directory).rglob(pattern):
                if log_file.is_file():
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            if log_file.suffix == '.json':
                                data = json.load(f)
                                if isinstance(data, dict):
                                    report["total_api_calls"] = data.get("total_calls", 0)
                                    report["cached_calls"] = data.get("cached_calls", 0)
                                    report["uncached_calls"] = data.get("uncached_calls", 0)
                                    report["estimated_tokens_saved"] = data.get("tokens_saved", 0)
                    except Exception as e:
                        pass
        
        # 计算缓存命中率
        if report["total_api_calls"] > 0:
            cache_hit_rate = (report["cached_calls"] / report["total_api_calls"]) * 100
            report["cache_hit_rate"] = f"{cache_hit_rate:.2f}%"
            
            if cache_hit_rate < 50:
                report["optimization_suggestions"].append({
                    "type": "increase_cache",
                    "priority": "high",
                    "description": "缓存命中率较低，建议增加缓存策略"
                })
            elif cache_hit_rate >= 80:
                report["optimization_suggestions"].append({
                    "type": "good_cache",
                    "priority": "info",
                    "description": "缓存策略良好，继续保持"
                })
        
        return report


def integrate_with_file_cleaner(cleaner, directory: str = ".") -> Dict[str, Any]:
    """
    将 API Token 优化集成到 File Cleaner 的主流程
    """
    optimizer = APITokenOptimizerIntegration()
    
    # 扫描 API 缓存
    api_cache = optimizer.scan_api_cache(directory)
    
    # 获取优化报告
    optimization_report = optimizer.get_optimization_report(directory)
    
    # 获取 Token 使用报告
    token_usage = optimizer.get_token_usage_report(directory)
    
    return {
        "api_cache_info": api_cache,
        "optimization_report": optimization_report,
        "token_usage_report": token_usage,
        "recommendations": optimization_report["recommendations"] + token_usage.get("optimization_suggestions", [])
    }


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 API Token Optimizer v2.0 集成测试")
    print("=" * 60)
    
    optimizer = APITokenOptimizerIntegration()
    
    # 测试扫描
    print("\n📊 扫描 API 缓存...")
    cache_info = optimizer.scan_api_cache(".")
    print(f"  缓存文件数：{len(cache_info['api_cache_files'])}")
    print(f"  总大小：{cache_info['total_size'] / 1024:.2f} KB")
    
    # 测试优化报告
    print("\n📈 优化报告...")
    report = optimizer.get_optimization_report(".")
    print(f"  建议数量：{len(report['recommendations'])}")
    for rec in report["recommendations"]:
        print(f"    - [{rec['priority']}] {rec['description']}")
    
    # 测试 Token 使用报告
    print("\n💰 Token 使用报告...")
    token_report = optimizer.get_token_usage_report(".")
    print(f"  总 API 调用：{token_report.get('total_api_calls', 0)}")
    print(f"  缓存命中：{token_report.get('cached_calls', 0)}")
    print(f"  建议：{len(token_report.get('optimization_suggestions', []))} 条")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成!")
    print("=" * 60)
