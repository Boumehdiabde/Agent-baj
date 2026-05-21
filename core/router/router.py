class AgentRouter:

    def __init__(self):
        self.agents = {
            "code": "coding-agent",
            "research": "research-agent",
            "marketing": "marketing-agent"
        }

    def handle(self, task):
        if "build" in task:
            return "coding-agent executing..."

        if "research" in task:
            return "research-agent executing..."

        return "default-agent"