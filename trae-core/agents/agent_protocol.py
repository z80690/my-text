# -*- coding: utf-8 -*-
"""
智能体间调用协议 - Agent Inter-Agent Communication Protocol

定义智能体之间的标准化通信接口和消息格式，
实现智能体间的无缝协作和联动。
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


# ============================================
# 消息类型枚举
# ============================================
class MessageType(Enum):
    """消息类型"""
    REQUEST = "request"           # 请求消息
    RESPONSE = "response"         # 响应消息
    ERROR = "error"               # 错误消息
    STATUS = "status"             # 状态消息
    BROADCAST = "broadcast"       # 广播消息
    COMMAND = "command"           # 命令消息
    EVENT = "event"               # 事件消息


class Priority(Enum):
    """消息优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(Enum):
    """动作类型"""
    EXECUTE = "execute"           # 执行任务
    QUERY = "query"               # 查询信息
    NOTIFY = "notify"             # 通知
    SUBSCRIBE = "subscribe"       # 订阅
    UNSUBSCRIBE = "unsubscribe"   # 取消订阅
    REGISTER = "register"         # 注册
    DEREGISTER = "deregister"     # 注销


# ============================================
# 消息协议定义
# ============================================
class AgentMessage:
    """智能体消息协议"""
    
    def __init__(
        self,
        action: str,
        source: str,
        target: str,
        payload: Dict[str, Any] = None,
        context_id: str = None,
        priority: str = "normal",
        msg_id: str = None
    ):
        self.msg_id = msg_id or str(uuid.uuid4())
        self.action = action
        self.source = source
        self.target = target
        self.payload = payload or {}
        self.context_id = context_id
        self.priority = priority
        self.timestamp = datetime.now().isoformat()
        self.metadata = {
            "retry_count": 0,
            "timeout": 30,
            "task_id": None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "msg_id": self.msg_id,
            "action": self.action,
            "source": self.source,
            "target": self.target,
            "payload": self.payload,
            "context_id": self.context_id,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """从字典创建消息"""
        msg = cls(
            action=data["action"],
            source=data["source"],
            target=data["target"],
            payload=data.get("payload", {}),
            context_id=data.get("context_id"),
            priority=data.get("priority", "normal"),
            msg_id=data.get("msg_id")
        )
        msg.timestamp = data.get("timestamp", datetime.now().isoformat())
        msg.metadata = data.get("metadata", {"retry_count": 0, "timeout": 30})
        return msg


# ============================================
# 智能体调用接口
# ============================================
class AgentCallInterface:
    """智能体调用接口"""
    
    def __init__(self, registry):
        self._registry = registry
        self._message_queue = []
        self._subscriptions = {}
    
    def call_agent(
        self,
        target_agent_id: str,
        task: str,
        context: Dict[str, Any] = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        调用指定智能体执行任务
        
        Args:
            target_agent_id: 目标智能体ID
            task: 任务内容
            context: 上下文信息
            priority: 优先级
        
        Returns:
            智能体执行结果
        """
        # 构建消息
        message = AgentMessage(
            action="execute",
            source="agent_call_interface",
            target=target_agent_id,
            payload={"task": task, "context": context or {}},
            priority=priority
        )
        
        # 发送消息并获取响应
        response = self._send_message(message)
        return response
    
    def broadcast(
        self,
        task: str,
        context: Dict[str, Any] = None,
        agent_filter: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        广播消息到多个智能体
        
        Args:
            task: 任务内容
            context: 上下文信息
            agent_filter: 智能体ID列表（可选，为空则广播到所有智能体）
        
        Returns:
            所有智能体的响应列表
        """
        results = []
        
        if agent_filter:
            agents = agent_filter
        else:
            agents = list(self._registry.get_all_agents().keys())
        
        for agent_id in agents:
            try:
                result = self.call_agent(agent_id, task, context)
                results.append(result)
            except Exception as e:
                results.append({
                    "agent_id": agent_id,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def chain_call(
        self,
        agent_chain: List[str],
        task: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        链式调用多个智能体
        
        Args:
            agent_chain: 智能体ID列表，按顺序调用
            task: 初始任务内容
            context: 上下文信息
        
        Returns:
            最终结果
        """
        current_result = {"task": task, "context": context or {}}
        
        for i, agent_id in enumerate(agent_chain):
            try:
                result = self.call_agent(
                    agent_id,
                    current_result.get("result", task),
                    current_result.get("context", {})
                )
                
                if result.get("status") == "success":
                    current_result = {
                        "step": i + 1,
                        "agent_id": agent_id,
                        "result": result.get("result", {}),
                        "context": {**current_result.get("context", {}), **result.get("result", {})}
                    }
                else:
                    current_result["error"] = result.get("error", "Unknown error")
                    break
            except Exception as e:
                current_result["error"] = str(e)
                break
        
        return current_result
    
    def parallel_call(
        self,
        agents: List[str],
        task: str,
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        并行调用多个智能体
        
        Args:
            agents: 智能体ID列表
            task: 任务内容
            context: 上下文信息
        
        Returns:
            所有智能体的响应列表
        """
        # 模拟并行执行（实际实现应使用异步）
        results = []
        
        for agent_id in agents:
            try:
                result = self.call_agent(agent_id, task, context)
                results.append(result)
            except Exception as e:
                results.append({
                    "agent_id": agent_id,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def subscribe(
        self,
        agent_id: str,
        event_type: str,
        callback
    ) -> bool:
        """
        订阅智能体事件
        
        Args:
            agent_id: 智能体ID
            event_type: 事件类型
            callback: 回调函数
        
        Returns:
            是否订阅成功
        """
        if agent_id not in self._subscriptions:
            self._subscriptions[agent_id] = {}
        
        if event_type not in self._subscriptions[agent_id]:
            self._subscriptions[agent_id][event_type] = []
        
        self._subscriptions[agent_id][event_type].append(callback)
        return True
    
    def notify(self, agent_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """
        通知订阅者事件发生
        
        Args:
            agent_id: 智能体ID
            event_type: 事件类型
            data: 事件数据
        """
        if agent_id in self._subscriptions:
            if event_type in self._subscriptions[agent_id]:
                for callback in self._subscriptions[agent_id][event_type]:
                    try:
                        callback(data)
                    except Exception:
                        pass
    
    def _send_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        发送消息到目标智能体
        
        Args:
            message: 消息对象
        
        Returns:
            响应结果
        """
        try:
            # 查找目标智能体
            agent = self._registry.get_agent(message.target)
            
            if not agent:
                return {
                    "status": "error",
                    "error": f"Agent {message.target} not found",
                    "msg_id": message.msg_id
                }
            
            # 执行智能体
            result = agent.execute(
                task=message.payload.get("task", ""),
                context=message.payload.get("context", {})
            )
            
            return {
                "status": "success",
                "msg_id": message.msg_id,
                "source": message.target,
                "result": result
            }
        
        except Exception as e:
            return {
                "status": "error",
                "msg_id": message.msg_id,
                "error": str(e)
            }


# ============================================
# 消息总线
# ============================================
class MessageBus:
    """消息总线 - 智能体间通信中枢"""
    
    def __init__(self):
        self._endpoints = {}
        self._middleware = []
    
    def register_endpoint(self, agent_id: str, handler) -> None:
        """
        注册消息处理端点
        
        Args:
            agent_id: 智能体ID
            handler: 消息处理函数
        """
        self._endpoints[agent_id] = handler
    
    def unregister_endpoint(self, agent_id: str) -> None:
        """
        注销消息处理端点
        
        Args:
            agent_id: 智能体ID
        """
        if agent_id in self._endpoints:
            del self._endpoints[agent_id]
    
    def add_middleware(self, middleware) -> None:
        """
        添加中间件
        
        Args:
            middleware: 中间件函数
        """
        self._middleware.append(middleware)
    
    def send(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """
        发送消息
        
        Args:
            message: 消息对象
        
        Returns:
            响应结果
        """
        # 执行中间件（发送前）
        for middleware in self._middleware:
            message = middleware("pre_send", message)
        
        # 处理消息
        if message.target in self._endpoints:
            try:
                response = self._endpoints[message.target](message)
                
                # 执行中间件（发送后）
                for middleware in self._middleware:
                    response = middleware("post_send", response)
                
                return response
            except Exception as e:
                return {
                    "status": "error",
                    "msg_id": message.msg_id,
                    "error": str(e)
                }
        elif message.target == "broadcast":
            # 广播消息
            results = []
            for agent_id, handler in self._endpoints.items():
                try:
                    result = handler(message)
                    results.append({"agent_id": agent_id, "result": result})
                except Exception as e:
                    results.append({"agent_id": agent_id, "error": str(e)})
            return {"status": "success", "results": results}
        
        return None


# ============================================
# 错误处理
# ============================================
class ProtocolError(Exception):
    """协议错误"""
    
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class ErrorCode(Enum):
    """错误码"""
    AGENT_UNAVAILABLE = "ERR_AGENT_UNAVAILABLE"
    TIMEOUT = "ERR_TIMEOUT"
    INVALID_MESSAGE = "ERR_INVALID_MESSAGE"
    PERMISSION_DENIED = "ERR_PERMISSION_DENIED"
    SERIALIZATION_ERROR = "ERR_SERIALIZATION_ERROR"


# ============================================
# 协议版本
# ============================================
PROTOCOL_VERSION = "1.0.0"

__all__ = [
    "MessageType",
    "Priority",
    "ActionType",
    "AgentMessage",
    "AgentCallInterface",
    "MessageBus",
    "ProtocolError",
    "ErrorCode",
    "PROTOCOL_VERSION"
]
