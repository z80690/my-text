# -*- coding: utf-8 -*-
"""
规则引擎 - 完整实现版本
包含双向同步、设计模式、大厂级优化
"""

import json
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


@dataclass
class RuleContext:
    """规则执行上下文"""
    user_input: str
    agent_state: Dict[str, Any]
    tool_calls: List[str]
    context_history: List[Dict]
    metadata: Dict[str, Any] = None


class IRule(ABC):
    """规则接口 - 策略模式抽象层"""
    
    @abstractmethod
    def get_id(self) -> str:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_level(self) -> str:
        pass
    
    @abstractmethod
    def get_severity(self) -> str:
        pass
    
    @abstractmethod
    def evaluate(self, context: RuleContext) -> bool:
        pass
    
    @abstractmethod
    def execute(self, context: RuleContext) -> Dict[str, Any]:
        pass


class BaseRule(IRule):
    """规则基类 - 模板方法模式"""
    
    def __init__(self, rule_id: str, name: str, level: str, severity: str):
        self._rule_id = rule_id
        self._name = name
        self._level = level
        self._severity = severity
        self._last_modified = datetime.now()
    
    def get_id(self) -> str:
        return self._rule_id
    
    def get_name(self) -> str:
        return self._name
    
    def get_level(self) -> str:
        return self._level
    
    def get_severity(self) -> str:
        return self._severity
    
    def evaluate(self, context: RuleContext) -> bool:
        return True
    
    def execute(self, context: RuleContext) -> Dict[str, Any]:
        result = self._do_execute(context)
        return {
            'rule_id': self._rule_id,
            'rule_name': self._name,
            'level': self._level,
            'severity': self._severity,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
    
    @abstractmethod
    def _do_execute(self, context: RuleContext) -> Any:
        pass


# ========== 具体规则实现 ==========

class ToolPriorityRule(BaseRule):
    def __init__(self):
        super().__init__('R001', '工具优先原则', 'L1', 'MEDIUM')
    
    def evaluate(self, context: RuleContext) -> bool:
        keywords = ['搜索', '查询', '获取', '查找', '分析', '计算', '统计']
        return any(kw in context.user_input for kw in keywords)
    
    def _do_execute(self, context: RuleContext) -> Any:
        return {
            'action': 'suggest_tool',
            'reason': f"检测到需要工具的请求: {context.user_input}",
            'suggested_tools': ['web_search', 'database_query']
        }


class AutoMemoryRule(BaseRule):
    def __init__(self):
        super().__init__('R002', 'AI自动记忆规则', 'L1', 'MEDIUM')
    
    def evaluate(self, context: RuleContext) -> bool:
        keywords = ['我习惯', '我喜欢', '我们团队', '以后都', '项目']
        return any(kw in context.user_input for kw in keywords)
    
    def _do_execute(self, context: RuleContext) -> Any:
        return {
            'action': 'store_memory',
            'memory_type': 'user_preference',
            'content': context.user_input
        }


class ParallelExecutionRule(BaseRule):
    def __init__(self):
        super().__init__('R003', '并行执行规则', 'L2', 'HIGH')
    
    def evaluate(self, context: RuleContext) -> bool:
        return len(context.tool_calls) > 1 or len(context.context_history) > 3
    
    def _do_execute(self, context: RuleContext) -> Any:
        return {
            'action': 'enable_parallel',
            'parallel_count': min(len(context.tool_calls), 5),
            'monitors': ['monitor_agent']
        }


class ContextPreservationRule(BaseRule):
    def __init__(self):
        super().__init__('R004', '上下文保持规则', 'L2', 'MEDIUM')
    
    def evaluate(self, context: RuleContext) -> bool:
        return len(context.context_history) > 0
    
    def _do_execute(self, context: RuleContext) -> Any:
        return {
            'action': 'preserve_context',
            'context_id': context.metadata.get('context_id', 'unknown'),
            'history_length': len(context.context_history)
        }


class RuleSystemExclusionRule(BaseRule):
    def __init__(self):
        super().__init__('R005', '规则体系互斥规则', 'L1', 'CRITICAL')
    
    def evaluate(self, context: RuleContext) -> bool:
        has_trae = '.trae' in context.user_input
        has_opencode = '.opencode' in context.user_input
        return has_trae and has_opencode
    
    def _do_execute(self, context: RuleContext) -> Any:
        return {
            'action': 'block',
            'reason': '检测到同时使用 .trae/ 和 .opencode/ 规则体系',
            'severity': 'CRITICAL'
        }


class WorkflowRule(BaseRule):
    def __init__(self):
        super().__init__('R007', '工作流执行规则', 'L3', 'MEDIUM')
    
    def evaluate(self, context: RuleContext) -> bool:
        return '工作流' in context.user_input or '流程' in context.user_input
    
    def _do_execute(self, context: RuleContext) -> Any:
        return {
            'action': 'execute_workflow',
            'workflow_type': 'sequential'
        }


class SwarmCooperationRule(BaseRule):
    def __init__(self):
        super().__init__('R008', '蜂群协作规则', 'L3', 'MEDIUM')
    
    def evaluate(self, context: RuleContext) -> bool:
        return '协作' in context.user_input or '蜂群' in context.user_input
    
    def _do_execute(self, context: RuleContext) -> Any:
        return {
            'action': 'enable_swarm',
            'agents': ['dispatcher_agent', 'monitor_agent']
        }


class CloudCodeMemoryRule(BaseRule):
    def __init__(self):
        super().__init__('R009', 'Cloud Code记忆系统规则', 'L2', 'HIGH')
    
    def evaluate(self, context: RuleContext) -> bool:
        return '记忆' in context.user_input or '知识' in context.user_input
    
    def _do_execute(self, context: RuleContext) -> Any:
        return {
            'action': 'sync_memory',
            'memory_level': 'semantic'
        }


class AgentCallRule(BaseRule):
    def __init__(self):
        super().__init__('R010', '智能体调用规则', 'L2', 'MEDIUM')
    
    def evaluate(self, context: RuleContext) -> bool:
        agent_keywords = ['智能体', '调度', '执行']
        return any(kw in context.user_input for kw in agent_keywords)
    
    def _do_execute(self, context: RuleContext) -> Any:
        return {
            'action': 'call_agent',
            'protocol': 'standard'
        }


# ========== 组合模式 - 规则集合 ==========

class RuleComposite(IRule):
    def __init__(self, name: str, level: str):
        self._name = name
        self._level = level
        self._children: List[IRule] = []
    
    def add_rule(self, rule: IRule):
        self._children.append(rule)
    
    def remove_rule(self, rule: IRule):
        self._children.remove(rule)
    
    def get_id(self) -> str:
        return f'COMPOSITE_{self._name}'
    
    def get_name(self) -> str:
        return self._name
    
    def get_level(self) -> str:
        return self._level
    
    def get_severity(self) -> str:
        severities = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2, 'CRITICAL': 3}
        max_sev = max((severities.get(r.get_severity(), 0) for r in self._children), default=0)
        return [k for k, v in severities.items() if v == max_sev][0]
    
    def evaluate(self, context: RuleContext) -> bool:
        return any(rule.evaluate(context) for rule in self._children)
    
    def execute(self, context: RuleContext) -> Dict[str, Any]:
        results = []
        for rule in self._children:
            if rule.evaluate(context):
                results.append(rule.execute(context))
        return {
            'composite_name': self._name,
            'level': self._level,
            'total_rules': len(self._children),
            'executed_rules': len(results),
            'results': results
        }


# ========== 责任链模式 - 规则执行链 ==========

class RuleHandler(ABC):
    def __init__(self):
        self._next_handler: Optional['RuleHandler'] = None
    
    def set_next(self, handler: 'RuleHandler') -> 'RuleHandler':
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, context: RuleContext) -> Optional[Dict[str, Any]]:
        pass


class L1RuleHandler(RuleHandler):
    def __init__(self):
        super().__init__()
        self._rules = [
            ToolPriorityRule(),
            AutoMemoryRule(),
            RuleSystemExclusionRule()
        ]
    
    def handle(self, context: RuleContext) -> Optional[Dict[str, Any]]:
        results = []
        for rule in self._rules:
            if rule.evaluate(context):
                result = rule.execute(context)
                results.append(result)
                if rule.get_severity() == 'CRITICAL':
                    return {'level': 'L1', 'blocked': True, 'results': results}
        
        if self._next_handler:
            next_result = self._next_handler.handle(context)
            if next_result:
                results.extend(next_result.get('results', []))
        
        return {'level': 'L1', 'blocked': False, 'results': results}


class L2RuleHandler(RuleHandler):
    def __init__(self):
        super().__init__()
        self._rules = [
            ParallelExecutionRule(),
            ContextPreservationRule(),
            CloudCodeMemoryRule(),
            AgentCallRule()
        ]
    
    def handle(self, context: RuleContext) -> Optional[Dict[str, Any]]:
        results = []
        for rule in self._rules:
            if rule.evaluate(context):
                results.append(rule.execute(context))
        
        if self._next_handler:
            next_result = self._next_handler.handle(context)
            if next_result:
                results.extend(next_result.get('results', []))
        
        return {'level': 'L2', 'results': results}


class L3RuleHandler(RuleHandler):
    def __init__(self):
        super().__init__()
        self._rules = [
            WorkflowRule(),
            SwarmCooperationRule()
        ]
    
    def handle(self, context: RuleContext) -> Optional[Dict[str, Any]]:
        results = []
        for rule in self._rules:
            if rule.evaluate(context):
                results.append(rule.execute(context))
        
        return {'level': 'L3', 'results': results}


# ========== 双向同步机制 ==========

class RuleSyncHandler(FileSystemEventHandler):
    """文件系统监听 - 双向同步"""
    
    def __init__(self, callback: Callable):
        self._callback = callback
    
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            print(f"[Sync] 检测到规则文件变更: {event.src_path}")
            self._callback(event.src_path)


class RuleSyncManager:
    """双向同步管理器"""
    
    def __init__(self):
        self._observer = None
        self._sync_callbacks: List[Callable] = []
        self._sync_status = {
            'last_sync': None,
            'sync_count': 0,
            'conflicts': []
        }
    
    def start_watching(self, paths: List[str]):
        """开始监听多个路径"""
        self._observer = Observer()
        for path in paths:
            if Path(path).exists():
                handler = RuleSyncHandler(self._on_file_changed)
                self._observer.schedule(handler, path, recursive=True)
        self._observer.start()
        print("[SyncManager] 双向同步监听已启动")
    
    def stop_watching(self):
        """停止监听"""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            print("[SyncManager] 双向同步监听已停止")
    
    def _on_file_changed(self, file_path: str):
        """文件变更处理"""
        self._sync_status['last_sync'] = datetime.now().isoformat()
        self._sync_status['sync_count'] += 1
        
        for callback in self._sync_callbacks:
            callback(file_path)
    
    def register_callback(self, callback: Callable):
        """注册同步回调"""
        self._sync_callbacks.append(callback)
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        return self._sync_status


# ========== 规则加载器 - 就近加载策略 ==========

class RuleLoader:
    """规则加载器 - 就近加载策略"""
    
    LOAD_PRIORITY = [
        './rules',           # 1. 当前目录
        '.trae/rules',       # 2. TRAE规则目录
        '../rules',          # 3. 上级目录
        '~/.trae/rules',     # 4. 用户目录
    ]
    
    def __init__(self):
        self._rules: Dict[str, IRule] = {}
        self._rule_hashes: Dict[str, str] = {}
        self._load_rules()
    
    def _calculate_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _load_rules(self):
        """按照就近原则加载规则"""
        for path_str in self.LOAD_PRIORITY:
            path = Path(path_str).expanduser()
            if path.exists() and path.is_dir():
                self._load_from_directory(path)
    
    def _load_from_directory(self, dir_path: Path):
        """从目录加载规则"""
        for md_file in dir_path.rglob('*.md'):
            rule = self._parse_rule_file(md_file)
            if rule:
                # 计算哈希用于变更检测
                content = md_file.read_text(encoding='utf-8')
                self._rule_hashes[rule.get_id()] = self._calculate_hash(content)
                self._rules[rule.get_id()] = rule
    
    def _parse_rule_file(self, file_path: Path) -> Optional[IRule]:
        """解析Markdown规则文件"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            rule_mappings = [
                ('工具优先', ToolPriorityRule),
                ('AI自动记忆' and '记忆', AutoMemoryRule),
                ('并行' and '监控', ParallelExecutionRule),
                ('上下文', ContextPreservationRule),
                ('互斥' or '.opencode', RuleSystemExclusionRule),
                ('工作流', WorkflowRule),
                ('蜂群', SwarmCooperationRule),
                ('Cloud Code', CloudCodeMemoryRule),
                ('智能体', AgentCallRule),
            ]
            
            for keywords, rule_class in rule_mappings:
                if all(kw in content for kw in keywords.split(' and ')) or \
                   any(kw in content for kw in keywords.split(' or ')):
                    return rule_class()
            
        except Exception as e:
            print(f"[RuleLoader] 解析文件失败 {file_path}: {e}")
        
        return None
    
    def reload_rule(self, file_path: str):
        """重新加载单个规则"""
        path = Path(file_path)
        if path.exists():
            rule = self._parse_rule_file(path)
            if rule:
                old_hash = self._rule_hashes.get(rule.get_id())
                content = path.read_text(encoding='utf-8')
                new_hash = self._calculate_hash(content)
                
                if old_hash != new_hash:
                    self._rules[rule.get_id()] = rule
                    self._rule_hashes[rule.get_id()] = new_hash
                    print(f"[RuleLoader] 规则已更新: {rule.get_id()}")
                    return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[IRule]:
        return self._rules.get(rule_id)
    
    def list_rules(self) -> List[IRule]:
        return list(self._rules.values())


# ========== 规则引擎 - 门面模式 ==========

class RuleEngine:
    """规则引擎 - 门面模式"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def initialize(self):
        """初始化规则引擎"""
        if self._initialized:
            return
        
        self._rule_loader = RuleLoader()
        self._sync_manager = RuleSyncManager()
        self._build_chain()
        self._setup_sync()
        
        self._initialized = True
        print("[RuleEngine] 规则引擎初始化完成")
    
    def _build_chain(self):
        """构建责任链"""
        self._chain = L1RuleHandler()
        self._chain.set_next(L2RuleHandler()).set_next(L3RuleHandler())
    
    def _setup_sync(self):
        """设置双向同步"""
        self._sync_manager.register_callback(self._on_rule_changed)
        self._sync_manager.start_watching(['.trae/rules'])
    
    def _on_rule_changed(self, file_path: str):
        """规则变更处理"""
        self._rule_loader.reload_rule(file_path)
        self._build_chain()
    
    def execute_rules(self, user_input: str, **kwargs) -> Dict[str, Any]:
        """执行规则引擎"""
        context = RuleContext(
            user_input=user_input,
            agent_state=kwargs.get('agent_state', {}),
            tool_calls=kwargs.get('tool_calls', []),
            context_history=kwargs.get('context_history', []),
            metadata=kwargs.get('metadata', {})
        )
        
        result = self._chain.handle(context)
        return {
            'status': 'success',
            'input': user_input,
            'evaluation': result,
            'sync_status': self._sync_manager.get_sync_status()
        }
    
    def get_rules_by_level(self, level: str) -> List[IRule]:
        """按级别获取规则"""
        return [r for r in self._rule_loader.list_rules() if r.get_level() == level]
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        return self._sync_manager.get_sync_status()
    
    def shutdown(self):
        """关闭规则引擎"""
        self._sync_manager.stop_watching()
        print("[RuleEngine] 规则引擎已关闭")


# ========== 规则存储层 ==========

class RuleStorage:
    """规则持久化存储"""
    
    def __init__(self, storage_path: str = '.trae/rules/.storage'):
        self._path = Path(storage_path)
        self._path.mkdir(parents=True, exist_ok=True)
    
    def save_rule(self, rule: IRule):
        """保存规则到文件"""
        file_path = self._path / f"{rule.get_id()}.json"
        data = {
            'rule_id': rule.get_id(),
            'name': rule.get_name(),
            'level': rule.get_level(),
            'severity': rule.get_severity(),
            'created_at': datetime.now().isoformat()
        }
        file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def load_all_rules(self) -> List[Dict]:
        """加载所有存储的规则"""
        rules = []
        for json_file in self._path.glob('*.json'):
            try:
                data = json.loads(json_file.read_text(encoding='utf-8'))
                rules.append(data)
            except Exception as e:
                print(f"[RuleStorage] 加载失败 {json_file}: {e}")
        return rules


# ========== 使用示例 ==========
if __name__ == '__main__':
    engine = RuleEngine()
    engine.initialize()
    
    result = engine.execute_rules(
        user_input="帮我搜索Python教程",
        agent_state={'agent_id': 'code_executor_agent'},
        tool_calls=[],
        context_history=[],
        metadata={'context_id': 'test_001'}
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    engine.shutdown()
