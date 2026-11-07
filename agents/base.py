"""Base agent implementation."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from core.llm import LLMProvider
from core.memory import ConversationMemory
from core.tools import CalculatorTool, FileTool, ToolRegistry


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, name: str, llm_provider: LLMProvider, memory: Optional[ConversationMemory] = None):
        self.name = name
        self.llm_provider = llm_provider
        self.memory = memory or ConversationMemory()
        self.tools = ToolRegistry()
        self.tools.register(CalculatorTool())
        self.tools.register(FileTool())

    @abstractmethod
    async def think(self, task: str) -> str:
        pass

    @abstractmethod
    async def act(self, plan: str) -> str:
        pass

    async def observe(self, result: str) -> str:
        self.memory.add("assistant", result)
        return result

    async def execute(self, task: str) -> str:
        self.memory.add("user", task)
        plan = await self.think(task)
        result = await self.act(plan)
        return await self.observe(result)

    async def chat_with_plan(self, instruction: str, plan: str) -> str:
        messages = [{"role": "system", "content": f"{instruction}\n\nPlan: {plan}"}]
        messages.extend(
            {"role": message.role, "content": message.content}
            for message in self.memory.retrieve(limit=10)
            if message.role in {"user", "assistant"}
        )
        response = await self.llm_provider.chat(messages)
        return response or ""

    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model_info": self.llm_provider.get_model_info(),
            "messages_in_memory": self.memory.get_message_count(),
            "tools_available": self.tools.list_tools(),
        }


class ResearchAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__("ResearchAgent", llm_provider)

    async def think(self, task: str) -> str:
        return await self.llm_provider.generate(f"Analyze this research task and create a research plan: {task}")

    async def act(self, plan: str) -> str:
        return await self.chat_with_plan("You are a research and analysis assistant. Be clear about uncertainty and do not invent sources.", plan)


class CodingAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__("CodingAgent", llm_provider)

    async def think(self, task: str) -> str:
        return await self.llm_provider.generate(f"Analyze this coding task and create a development plan: {task}")

    async def act(self, plan: str) -> str:
        return await self.chat_with_plan("You are a coding assistant. Provide safe, testable code and explain assumptions.", plan)


class AutomationAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__("AutomationAgent", llm_provider)

    async def think(self, task: str) -> str:
        return await self.llm_provider.generate(f"Analyze this automation task and create an automation plan: {task}")

    async def act(self, plan: str) -> str:
        return await self.chat_with_plan("You design automation workflows. Do not claim to execute workflows.", plan)


class MarketingAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__("MarketingAgent", llm_provider)

    async def think(self, task: str) -> str:
        return await self.llm_provider.generate(f"Analyze this marketing task and create a marketing strategy: {task}")

    async def act(self, plan: str) -> str:
        return await self.chat_with_plan("You are a marketing assistant. Tailor recommendations to the supplied context.", plan)
