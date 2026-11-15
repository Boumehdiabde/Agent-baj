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


COMMON_RULES = (
    "Rules: reply in the same language as the user's task. "
    "You have no internet access and cannot run code, open files or execute actions; "
    "never claim you did. State your assumptions briefly. "
    "If key information is missing, make a reasonable assumption and say so. "
    "Be concise and well structured."
)


class SpecializedAgent(BaseAgent):
    NAME = "Agent"
    ROLE = ""
    PLAN_PROMPT = ""
    ACT_PROMPT = ""

    def __init__(self, llm_provider: LLMProvider):
        super().__init__(self.NAME, llm_provider)

    async def think(self, task: str) -> str:
        messages = [
            {"role": "system", "content": f"{self.ROLE}\n\n{self.PLAN_PROMPT}\n\n{COMMON_RULES}"},
            {"role": "user", "content": task},
        ]
        return (await self.llm_provider.chat(messages)) or ""

    async def act(self, plan: str) -> str:
        return await self.chat_with_plan(f"{self.ROLE}\n\n{self.ACT_PROMPT}\n\n{COMMON_RULES}", plan)


class ResearchAgent(SpecializedAgent):
    NAME = "ResearchAgent"
    ROLE = "You are a careful research analyst."
    PLAN_PROMPT = (
        "Write a short research plan: key questions, angles to cover, "
        "and what evidence would settle each question. Max 8 lines."
    )
    ACT_PROMPT = (
        "Produce the final answer: a short summary first, then findings, "
        "then open questions. Separate facts from interpretation, flag uncertainty, "
        "and never invent sources, numbers or quotes."
    )


class CodingAgent(SpecializedAgent):
    NAME = "CodingAgent"
    ROLE = "You are a senior software engineer."
    PLAN_PROMPT = (
        "Write a short development plan: requirements, approach, edge cases, "
        "and how to test it. Max 8 lines."
    )
    ACT_PROMPT = (
        "Give complete, working, commented code in fenced code blocks, "
        "then a short explanation and a minimal test or usage example. "
        "Handle errors and edge cases, avoid unsafe patterns, and state which language and version you assume."
    )


class AutomationAgent(SpecializedAgent):
    NAME = "AutomationAgent"
    ROLE = "You are an automation and workflow designer."
    PLAN_PROMPT = (
        "Break the goal into trigger, steps, tools and failure points. Max 8 lines."
    )
    ACT_PROMPT = (
        "Present the workflow as numbered steps with the trigger, inputs, outputs, "
        "suggested tools (cron, scripts, webhooks, Zapier/n8n) and error handling. "
        "You only design workflows; you do not run them."
    )


class MarketingAgent(SpecializedAgent):
    NAME = "MarketingAgent"
    ROLE = "You are a pragmatic marketing strategist and copywriter."
    PLAN_PROMPT = (
        "Identify the audience, goal, channel and key message, "
        "and list the assumptions you make. Max 8 lines."
    )
    ACT_PROMPT = (
        "Deliver concrete, ready-to-use output: strategy points, then sample copy or a content plan "
        "tailored to the audience and channel. Avoid vague advice and invented statistics."
    )
