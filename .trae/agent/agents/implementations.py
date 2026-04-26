from typing import Dict, Any
from .base import BaseAgent, AgentConfig
import os
import requests

# 大模型配置
OPENAI_API_KEY = os.environ.get("BOCHA_API_KEY") or os.environ.get("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.baichuan-ai.com/v1/chat/completions"  # 使用Bocha API

class LLMClient:
    """大模型客户端"""
    
    @staticmethod
    def call_llm(system_prompt: str, user_prompt: str) -> str:
        """调用大模型（模拟）"""
        if not OPENAI_API_KEY:
            # 模拟大模型响应
            return f"[模拟大模型响应]\n系统提示: {system_prompt[:50]}...\n用户任务: {user_prompt[:50]}...\n这是一个模拟的大模型响应，展示智能体的工作原理。在实际使用中，这里会调用真实的大模型API。"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        payload = {
            "model": "Baichuan4-Turbo",  # 使用Bocha模型
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            return f"大模型调用失败: {str(e)}"

AGENT_CONFIGS = {
    "assistant_agent": AgentConfig(
        id="assistant_agent",
        name="Assistant Agent",
        description="通用助手智能体",
        type="autogen_agentchat",
        capabilities=["chat", "general", "assistant"]
    ),
    "user_proxy_agent": AgentConfig(
        id="user_proxy_agent",
        name="User Proxy Agent",
        description="用户代理智能体",
        type="autogen_agentchat",
        capabilities=["user", "proxy", "interaction"]
    ),
    "code_executor_agent": AgentConfig(
        id="code_executor_agent",
        name="Code Executor Agent",
        description="代码执行智能体",
        type="autogen_agentchat",
        capabilities=["code", "execution", "programming"]
    ),
    "message_filter_agent": AgentConfig(
        id="message_filter_agent",
        name="Message Filter Agent",
        description="消息过滤智能体",
        type="autogen_agentchat",
        capabilities=["filter", "message", "processing"]
    ),
    "society_of_mind_agent": AgentConfig(
        id="society_of_mind_agent",
        name="Society of Mind Agent",
        description="心智社会智能体",
        type="autogen_agentchat",
        capabilities=["reasoning", "cognitive", "multi_agent"]
    ),
    "base_agent": AgentConfig(
        id="base_agent",
        name="Base Agent",
        description="基础智能体",
        type="autogen_core",
        capabilities=["base", "foundation"]
    ),
    "closure_agent": AgentConfig(
        id="closure_agent",
        name="Closure Agent",
        description="闭包智能体",
        type="autogen_core",
        capabilities=["closure", "encapsulation"]
    ),
    "routed_agent": AgentConfig(
        id="routed_agent",
        name="Routed Agent",
        description="路由智能体",
        type="autogen_core",
        capabilities=["routing", "dispatch"]
    ),
    "tool_agent": AgentConfig(
        id="tool_agent",
        name="Tool Agent",
        description="工具智能体",
        type="autogen_core",
        capabilities=["tools", "execution"]
    ),
    "chess_agent": AgentConfig(
        id="chess_agent",
        name="Chess Agent",
        description="国际象棋智能体",
        type="sample",
        capabilities=["game", "chess", "strategy"]
    ),
    "fastapi_agent": AgentConfig(
        id="fastapi_agent",
        name="FastAPI Agent",
        description="FastAPI智能体",
        type="sample",
        capabilities=["api", "fastapi", "web"]
    ),
    "streamlit_agent": AgentConfig(
        id="streamlit_agent",
        name="Streamlit Agent",
        description="Streamlit智能体",
        type="sample",
        capabilities=["ui", "streamlit", "visualization"]
    ),
    "graphrag_agent": AgentConfig(
        id="graphrag_agent",
        name="GraphRAG Agent",
        description="GraphRAG智能体",
        type="sample",
        capabilities=["graph", "rag", "knowledge"]
    ),
    "dspy_agent": AgentConfig(
        id="dspy_agent",
        name="DSPy Agent",
        description="DSPy智能体",
        type="sample",
        capabilities=["dspy", "programming", "ai"]
    ),
    "xlang_agent": AgentConfig(
        id="xlang_agent",
        name="Cross-language Agent",
        description="跨语言智能体",
        type="sample",
        capabilities=["multilingual", "translation", "cross_language"]
    ),
    "semantic_router_agent": AgentConfig(
        id="semantic_router_agent",
        name="Semantic Router Agent",
        description="语义路由智能体",
        type="sample",
        capabilities=["semantic", "routing", "nlp"]
    ),
    "editor_agent": AgentConfig(
        id="editor_agent",
        name="Editor Agent",
        description="编辑器智能体",
        type="sample",
        capabilities=["edit", "writing", "text"]
    ),
    "writer_agent": AgentConfig(
        id="writer_agent",
        name="Writer Agent",
        description="作家智能体",
        type="sample",
        capabilities=["write", "creative", "content"]
    ),
    "teachable_agent": AgentConfig(
        id="teachable_agent",
        name="Teachable Agent",
        description="可教学智能体",
        type="sample",
        capabilities=["teach", "learn", "adaptive"]
    ),
    "grpc_agent": AgentConfig(
        id="grpc_agent",
        name="gRPC Agent",
        description="gRPC智能体",
        type="sample",
        capabilities=["grpc", "rpc", "api"]
    ),
}

class AssistantAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个专业的通用助手智能体。你的职责是帮助用户解决各种问题，提供准确、有用的信息和建议。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "assistant", "llm_enhanced": True}

class UserProxyAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个用户代理智能体，专门处理和转发用户请求。你的职责是理解用户的需求，并以适当的方式处理这些请求。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "proxy", "llm_enhanced": True}

class CodeExecutorAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个代码执行智能体，专门执行各种编程语言的代码。你的职责是分析代码，解释代码功能，并提供执行建议。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "code_execution", "llm_enhanced": True}

class MessageFilterAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个消息过滤智能体，专门处理和过滤各种消息内容。你的职责是分析消息，提取关键信息，并根据需要进行过滤和处理。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "filter", "llm_enhanced": True}

class SocietyOfMindAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个心智社会智能体，具有高级推理和认知能力。你的职责是通过多维度思考分析问题，提供深度洞察和解决方案。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "cognitive", "llm_enhanced": True}

class BaseAgentImpl(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个基础智能体，提供基本的任务处理能力。你的职责是处理各种基础任务，提供通用的解决方案。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "base", "llm_enhanced": True}

class ClosureAgentImpl(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个闭包智能体，专门处理与闭包和封装相关的任务。你的职责是提供关于闭包概念、实现和应用的专业知识。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "closure", "llm_enhanced": True}

class RoutedAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个路由智能体，专门负责任务的路由和分发。你的职责是分析任务性质，将其路由到最合适的处理方。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "routing", "llm_enhanced": True}

class ToolAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个工具智能体，专门使用各种工具来执行任务。你的职责是选择合适的工具，有效地执行任务，并提供详细的执行结果。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "tool", "llm_enhanced": True}

class ChessAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个国际象棋智能体，专门处理与国际象棋相关的任务。你的职责是提供国际象棋的分析、策略和建议。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "chess", "llm_enhanced": True}

class FastAPIAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个FastAPI智能体，专门处理与FastAPI框架相关的任务。你的职责是提供FastAPI的开发、配置和最佳实践建议。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "fastapi", "llm_enhanced": True}

class StreamlitAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个Streamlit智能体，专门处理与Streamlit框架相关的任务。你的职责是提供Streamlit应用的开发、设计和最佳实践建议。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "streamlit", "llm_enhanced": True}

class GraphRAGAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个GraphRAG智能体，专门处理与知识图谱和检索增强生成相关的任务。你的职责是提供GraphRAG的设计、实现和应用建议。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "graphrag", "llm_enhanced": True}

class DSPyAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个DSPy智能体，专门处理与DSPy框架相关的任务。你的职责是提供DSPy的使用、优化和最佳实践建议。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "dspy", "llm_enhanced": True}

class XLangAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个跨语言智能体，专门处理多语言翻译和跨语言交流任务。你的职责是提供准确、流畅的翻译服务和跨语言沟通支持。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "xlang", "llm_enhanced": True}

class SemanticRouterAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个语义路由智能体，专门根据任务的语义内容进行智能路由。你的职责是分析任务的语义，将其路由到最合适的处理方。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "semantic", "llm_enhanced": True}

class EditorAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个编辑器智能体，专门处理文本编辑和内容优化任务。你的职责是提供专业的编辑服务，确保文本内容的质量和准确性。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "editor", "llm_enhanced": True}

class WriterAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个作家智能体，专门创作各种类型的内容。你的职责是根据用户的需求，创作高质量、有创意的内容。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "writer", "llm_enhanced": True}

class TeachableAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个可教学智能体，具有学习和适应能力。你的职责是通过学习不断提高自己的能力，适应新的任务和环境。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "teachable", "llm_enhanced": True}

class GRPCAgent(BaseAgent):
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        system_prompt = "你是一个gRPC智能体，专门处理与gRPC框架相关的任务。你的职责是提供gRPC的设计、实现和最佳实践建议。"
        response = LLMClient.call_llm(system_prompt, task)
        return {"response": response, "type": "grpc", "llm_enhanced": True}

def get_all_agents():
    return [
        AssistantAgent(AGENT_CONFIGS["assistant_agent"]),
        UserProxyAgent(AGENT_CONFIGS["user_proxy_agent"]),
        CodeExecutorAgent(AGENT_CONFIGS["code_executor_agent"]),
        MessageFilterAgent(AGENT_CONFIGS["message_filter_agent"]),
        SocietyOfMindAgent(AGENT_CONFIGS["society_of_mind_agent"]),
        BaseAgentImpl(AGENT_CONFIGS["base_agent"]),
        ClosureAgentImpl(AGENT_CONFIGS["closure_agent"]),
        RoutedAgent(AGENT_CONFIGS["routed_agent"]),
        ToolAgent(AGENT_CONFIGS["tool_agent"]),
        ChessAgent(AGENT_CONFIGS["chess_agent"]),
        FastAPIAgent(AGENT_CONFIGS["fastapi_agent"]),
        StreamlitAgent(AGENT_CONFIGS["streamlit_agent"]),
        GraphRAGAgent(AGENT_CONFIGS["graphrag_agent"]),
        DSPyAgent(AGENT_CONFIGS["dspy_agent"]),
        XLangAgent(AGENT_CONFIGS["xlang_agent"]),
        SemanticRouterAgent(AGENT_CONFIGS["semantic_router_agent"]),
        EditorAgent(AGENT_CONFIGS["editor_agent"]),
        WriterAgent(AGENT_CONFIGS["writer_agent"]),
        TeachableAgent(AGENT_CONFIGS["teachable_agent"]),
        GRPCAgent(AGENT_CONFIGS["grpc_agent"]),
    ]

def register_all_agents(registry):
    for agent in get_all_agents():
        registry.register(agent)
