"""Base agent implementation"""
from abc import ABC, abstractmethod
from core.llm import get_llm_provider, LLMProvider
from core.memory import ConversationMemory
from core.tools import ToolRegistry
from typing import Optional, Dict, Any


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, llm_provider: LLMProvider, memory: Optional[ConversationMemory] = None):
        self.name = name
        self.llm_provider = llm_provider
        self.memory = memory or ConversationMemory()
        self.tools = ToolRegistry()
    
    @abstractmethod
    async def think(self, task: str) -> str:
        """Thinking phase - analyze the task"""
        pass
    
    @abstractmethod
    async def act(self, plan: str) -> str:
        """Action phase - execute the plan"""
        pass
    
    async def observe(self, result: str) -> str:
        """Observation phase - analyze results"""
        self.memory.add("assistant", result)
        return result
    
    async def execute(self, task: str) -> str:
        """Execute task using Think-Act-Observe cycle"""
        # Think
        self.memory.add("user", task)
        thinking = await self.think(task)
        self.memory.add("system", f"Thinking: {thinking}")
        
        # Act
        action = await self.act(thinking)
        self.memory.add("system", f"Action: {action}")
        
        # Observe
        result = await self.observe(action)
        
        return result
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent"""
        return {
            "name": self.name,
            "model_info": self.llm_provider.get_model_info(),
            "messages_in_memory": self.memory.get_message_count(),
            "tools_available": self.tools.list_tools()
        }


class ResearchAgent(BaseAgent):
    """Agent specialized in research and analysis"""
    
    def __init__(self, llm_provider: LLMProvider):
        super().__init__("ResearchAgent", llm_provider)
    
    async def think(self, task: str) -> str:
        """Analyze research task"""
        prompt = f"Analyze this research task and create a research plan: {task}"
        return await self.llm_provider.generate(prompt)
    
    async def act(self, plan: str) -> str:
        """Execute research plan"""
        prompt = f"Based on this research plan, provide analysis: {plan}"
        messages = self.memory.retrieve(limit=10)
        return await self.llm_provider.chat([
            {"role": "user", "content": prompt}
        ])


class CodingAgent(BaseAgent):
    """Agent specialized in coding tasks"""
    
    def __init__(self, llm_provider: LLMProvider):
        super().__init__("CodingAgent", llm_provider)
    
    async def think(self, task: str) -> str:
        """Analyze coding task"""
        prompt = f"Analyze this coding task and create a development plan: {task}"
        return await self.llm_provider.generate(prompt)
    
    async def act(self, plan: str) -> str:
        """Execute coding plan"""
        prompt = f"Based on this development plan, generate code: {plan}"
        return await self.llm_provider.chat([
            {"role": "user", "content": prompt}
        ])


class AutomationAgent(BaseAgent):
    """Agent specialized in workflow automation"""
    
    def __init__(self, llm_provider: LLMProvider):
        super().__init__("AutomationAgent", llm_provider)
    
    async def think(self, task: str) -> str:
        """Analyze automation task"""
        prompt = f"Analyze this automation task and create an automation plan: {task}"
        return await self.llm_provider.generate(prompt)
    
    async def act(self, plan: str) -> str:
        """Execute automation plan"""
        prompt = f"Based on this automation plan, generate workflow configuration: {plan}"
        return await self.llm_provider.chat([
            {"role": "user", "content": prompt}
        ])


class MarketingAgent(BaseAgent):
    """Agent specialized in marketing campaigns"""
    
    def __init__(self, llm_provider: LLMProvider):
        super().__init__("MarketingAgent", llm_provider)
    
    async def think(self, task: str) -> str:
        """Analyze marketing task"""
        prompt = f"Analyze this marketing task and create a marketing strategy: {task}"
        return await self.llm_provider.generate(prompt)
    
    async def act(self, plan: str) -> str:
        """Execute marketing plan"""
        prompt = f"Based on this marketing strategy, generate campaign content: {plan}"
        return await self.llm_provider.chat([
            {"role": "user", "content": prompt}
        ])
