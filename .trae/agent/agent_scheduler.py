import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .agents import get_registry, register_all_agents, BaseAgent

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

@dataclass
class Agent:
    id: str
    name: str
    capabilities: List[str]
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    completed_tasks: int = 0
    failed_tasks: int = 0
    is_agent_framework: bool = False

@dataclass
class AgentTask:
    id: str
    description: str
    required_capability: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: str = "pending"
    assigned_agent: Optional[str] = None
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

class AgentScheduler:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self.task_queue: List[str] = []
        self.task_results: Dict[str, Any] = {}
        self.agent_registry = get_registry()
        self._load_agents()

    def _load_agents(self):
        register_all_agents(self.agent_registry)
        for agent in self.agent_registry.list_agents():
            scheduler_agent = Agent(
                id=agent["id"],
                name=agent["name"],
                capabilities=["general"],
                is_agent_framework=False
            )
            self.register_agent(scheduler_agent)
        print(f"Loaded {len(self.agents)} agents from registry")
        
    def register_agent(self, agent: Agent):
        self.agents[agent.id] = agent
        print(f"Agent registered: {agent.name} ({agent.id})")
        
    def unregister_agent(self, agent_id: str):
        if agent_id in self.agents:
            del self.agents[agent_id]
            print(f"Agent unregistered: {agent_id}")
            
    def submit_task(self, task: AgentTask):
        self.tasks[task.id] = task
        self.task_queue.append(task.id)
        print(f"Task submitted: {task.description} (priority: {task.priority.name})")
        
    def get_task(self, task_id: str) -> Optional[AgentTask]:
        return self.tasks.get(task_id)
    
    def find_available_agent(self, required_capability: str) -> Optional[Agent]:
        for agent in self.agents.values():
            if (agent.status == AgentStatus.IDLE and 
                required_capability in agent.capabilities):
                return agent
        return None
    
    async def assign_tasks(self):
        while self.task_queue:
            task_id = self.task_queue.pop(0)
            task = self.tasks[task_id]
            
            agent = self.find_available_agent(task.required_capability)
            if agent:
                await self._execute_task(agent, task)
            else:
                print(f"No available agent for task: {task.description}")
                self.task_queue.append(task_id)
                await asyncio.sleep(1)
    
    async def _execute_task(self, agent: Agent, task: AgentTask):
        agent.status = AgentStatus.BUSY
        agent.current_task = task.id
        task.assigned_agent = agent.id
        task.status = "running"
        
        print(f"Task assigned: {task.description} -> {agent.name}")
        
        try:
            result = await self._run_agent_task(agent, task)
            
            task.result = result
            task.status = "completed"
            agent.completed_tasks += 1
            self.task_results[task.id] = result
            
            print(f"Task completed: {task.description} - {agent.name}")
            
        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            agent.failed_tasks += 1
            print(f"Task failed: {task.description} - {str(e)}")
            
        finally:
            agent.status = AgentStatus.IDLE
            agent.current_task = None
    
    async def _run_agent_task(self, agent: Agent, task: AgentTask) -> Any:
        await asyncio.sleep(0.1)
        result = self.agent_registry.execute(agent.id, task.description)
        if result.get("status") == "success":
            return result.get("result")
        else:
            raise Exception(result.get("message", f"Agent {agent.name} failed to execute"))
    
    async def _run_agent_framework_task(self, agent: Agent, task: AgentTask) -> Any:
        result = self.agent_framework.execute_agent(agent.id, task.description)
        if result.get("status") == "success":
            return result.get("result")
        else:
            raise Exception(result.get("message", "Failed to execute agent framework task"))
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        return {
            "agents": {
                agent_id: {
                    "name": agent.name,
                    "status": agent.status.value,
                    "current_task": agent.current_task,
                    "completed_tasks": agent.completed_tasks,
                    "failed_tasks": agent.failed_tasks,
                    "is_agent_framework": agent.is_agent_framework
                }
                for agent_id, agent in self.agents.items()
            },
            "tasks": {
                task_id: {
                    "description": task.description,
                    "status": task.status,
                    "assigned_agent": task.assigned_agent,
                    "priority": task.priority.name
                }
                for task_id, task in self.tasks.items()
            },
            "queue_length": len(self.task_queue)
        }
    
    def get_task_results(self) -> Dict[str, Any]:
        return self.task_results
    
    def reset_scheduler(self):
        for agent in self.agents.values():
            agent.status = AgentStatus.IDLE
            agent.current_task = None
            agent.completed_tasks = 0
            agent.failed_tasks = 0
        
        self.tasks.clear()
        self.task_queue.clear()
        self.task_results.clear()
        print("Scheduler reset")