"""Agent router for task routing and orchestration"""
from typing import List, Dict, Any
from core.memory import ConversationMemory


class AgentRouter:
    """Routes tasks to appropriate agents"""
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.route_keywords = {
            "research": ["research", "analyze", "investigate", "study", "explore", "find"],
            "coding": ["code", "debug", "develop", "implement", "fix", "program", "script"],
            "automation": ["automate", "schedule", "workflow", "process", "batch", "repeat"],
            "marketing": ["market", "campaign", "promote", "advertise", "content", "strategy"]
        }
    
    def analyze_task(self, task: str) -> str:
        """Analyze task and determine agent type"""
        task_lower = task.lower()
        
        # Count keyword matches for each agent type
        scores = {}
        for agent_type, keywords in self.route_keywords.items():
            score = sum(1 for keyword in keywords if keyword in task_lower)
            scores[agent_type] = score
        
        # Return agent with highest score, default to research
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "research"
    
    def route_task(self, task: str, agent_type: str = None) -> Dict[str, Any]:
        """Route task to appropriate agent"""
        if agent_type is None:
            agent_type = self.analyze_task(task)
        
        # Store in memory
        self.memory.add("user", task)
        
        return {
            "agent_type": agent_type,
            "task": task,
            "context": self.memory.get_context()
        }
    
    def get_agent_description(self, agent_type: str) -> str:
        """Get description of agent type"""
        descriptions = {
            "research": "Handles research, analysis, and information gathering tasks",
            "coding": "Handles code generation, debugging, and development tasks",
            "automation": "Handles workflow automation and scheduling tasks",
            "marketing": "Handles marketing campaigns and content creation tasks"
        }
        return descriptions.get(agent_type, "Unknown agent type")
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            "total_messages": self.memory.get_message_count(),
            "conversation_length": self.memory.get_conversation_length(),
            "available_agents": list(self.route_keywords.keys())
        }
