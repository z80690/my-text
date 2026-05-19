"""
Auto Memory Skill Implementation
自动记忆技能实现
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Optional, Any

class RuleLogger:
    """规则执行日志记录器"""
    
    def __init__(self):
        self.log_file = ".trae/memories/project/rule_execution_logs.json"
        self._ensure_dir()
        self._init_log_file()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def _init_log_file(self):
        """初始化日志文件"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "logs": [],
                    "statistics": {
                        "total_executions": 0,
                        "success_rate": 0,
                        "coverage_rate": 0,
                        "optimization_rate": 0
                    },
                    "last_updated": ""
                }, f, ensure_ascii=False, indent=2)
    
    def log_execution(self, rule_id: str, condition: str, action: str, result: str, success: bool = True, details: str = ""):
        """记录规则执行日志"""
        log_entry = {
            "rule_id": rule_id,
            "timestamp": datetime.now().isoformat(),
            "condition": condition,
            "action": action,
            "result": result,
            "success": success,
            "details": details
        }
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data["logs"].append(log_entry)
        data["statistics"]["total_executions"] += 1
        data["last_updated"] = datetime.now().isoformat()
        
        # 计算成功率
        success_count = sum(1 for log in data["logs"] if log["success"])
        if data["statistics"]["total_executions"] > 0:
            data["statistics"]["success_rate"] = round(success_count / data["statistics"]["total_executions"] * 100, 2)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计数据"""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data["statistics"]
        return {}
    
    def generate_optimization_suggestions(self) -> list:
        """生成优化建议"""
        stats = self.get_statistics()
        suggestions = []
        
        if stats.get("success_rate", 100) < 90:
            suggestions.append({
                "priority": "high",
                "rule_id": "all",
                "suggestion": f"规则执行成功率 {stats['success_rate']}%，低于90%阈值，建议检查规则可执行性",
                "action": "Review L2.10规则可执行性要求"
            })
        
        if stats.get("total_executions", 0) > 100:
            suggestions.append({
                "priority": "medium",
                "rule_id": "all",
                "suggestion": "规则执行次数超过100次，建议进行规则效果评估",
                "action": "分析规则执行日志，识别低效规则"
            })
        
        return suggestions

class ContextManager:
    """上下文管理器"""
    
    def __init__(self):
        self.context_file = ".trae/memories/project/context_pointer.json"
        self._ensure_dir()
        self._init_context()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.context_file), exist_ok=True)
    
    def _init_context(self):
        """初始化上下文文件"""
        if not os.path.exists(self.context_file):
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "current_focus": "",
                    "recent_changes": [],
                    "known_issues": [],
                    "last_updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
    
    def update_context(self, focus: str = None, changes: list = None, issues: list = None):
        """更新上下文指针"""
        with open(self.context_file, 'r', encoding='utf-8') as f:
            context = json.load(f)
        
        if focus:
            context["current_focus"] = focus
        
        if changes:
            for change in changes:
                context["recent_changes"].insert(0, {
                    "change": change,
                    "timestamp": datetime.now().isoformat()
                })
            # 保留最近10条变更
            context["recent_changes"] = context["recent_changes"][:10]
        
        if issues:
            context["known_issues"] = list(set(context["known_issues"] + issues))
        
        context["last_updated"] = datetime.now().isoformat()
        
        with open(self.context_file, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=2)
    
    def get_context(self) -> Dict[str, Any]:
        """获取当前上下文"""
        if os.path.exists(self.context_file):
            with open(self.context_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

def process_message(message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    处理用户消息并记录到记忆系统
    
    Args:
        message: 用户消息内容
        context: 上下文信息（可选）
    
    Returns:
        {"status": "success", "memory_file": "文件路径", "message_length": 长度}
    """
    # 确保目录存在
    memory_dir = ".trae/memories/user"
    os.makedirs(memory_dir, exist_ok=True)
    
    # 生成记忆文件路径
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存消息到记忆文件
    memory_data = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "context": context or {},
        "processed": True
    }
    
    memory_file = os.path.join(memory_dir, f"memory_{timestamp}.json")
    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(memory_data, f, ensure_ascii=False, indent=2)
    
    # 记录规则执行日志
    logger = RuleLogger()
    logger.log_execution(
        rule_id="L2.3",
        condition="用户发送消息",
        action="记录消息到记忆系统",
        result=f"消息长度: {len(message)}",
        success=True
    )
    
    # 更新上下文
    ctx_manager = ContextManager()
    ctx_manager.update_context(
        focus="消息处理",
        changes=[f"记录消息: {message[:50]}..." if len(message) > 50 else f"记录消息: {message}"]
    )
    
    return {
        "status": "success",
        "memory_file": memory_file,
        "message_length": len(message),
        "timestamp": datetime.now().isoformat()
    }

def get_statistics() -> Dict[str, Any]:
    """获取规则执行统计"""
    logger = RuleLogger()
    return logger.get_statistics()

def get_suggestions() -> list:
    """获取规则优化建议"""
    logger = RuleLogger()
    return logger.generate_optimization_suggestions()

def get_context() -> Dict[str, Any]:
    """获取上下文指针"""
    ctx_manager = ContextManager()
    return ctx_manager.get_context()

# 测试函数
def test_skill():
    """测试自动记忆技能"""
    print("=== 测试自动记忆技能 ===")
    
    # 测试消息记录
    result = process_message("测试自动记忆技能", {"test": "true"})
    print(f"1. 消息记录: {result['status']}")
    print(f"   文件: {result['memory_file']}")
    print(f"   长度: {result['message_length']}")
    
    # 测试统计获取
    stats = get_statistics()
    print(f"\n2. 统计数据:")
    print(f"   总执行次数: {stats.get('total_executions', 0)}")
    print(f"   成功率: {stats.get('success_rate', 0)}%")
    
    # 测试建议获取
    suggestions = get_suggestions()
    print(f"\n3. 优化建议: {len(suggestions)} 条")
    
    # 测试上下文获取
    ctx = get_context()
    print(f"\n4. 上下文:")
    print(f"   当前焦点: {ctx.get('current_focus', '')}")
    print(f"   最近变更数: {len(ctx.get('recent_changes', []))}")
    
    print("\n=== 测试完成 ===")
    return True

if __name__ == "__main__":
    test_skill()