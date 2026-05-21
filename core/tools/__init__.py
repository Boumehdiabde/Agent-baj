"""Tools system for agents"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List, Optional
import json


class Tool(ABC):
    """Abstract base class for tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for the tool"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }


class ToolRegistry:
    """Registry for managing and executing tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool"""
        self.tools[tool.name] = tool
    
    def unregister(self, name: str) -> None:
        """Unregister a tool"""
        if name in self.tools:
            del self.tools[name]
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    async def execute(self, name: str, **kwargs) -> str:
        """Execute a tool by name"""
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        try:
            return await tool.execute(**kwargs)
        except Exception as e:
            return f"Error executing {name}: {str(e)}"
    
    def list_tools(self) -> List[str]:
        """List all registered tools"""
        return list(self.tools.keys())
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get schemas for all tools"""
        return [tool.get_schema() for tool in self.tools.values()]


# Built-in tools

class SearchTool(Tool):
    """Tool for searching information"""
    
    def __init__(self):
        super().__init__(
            name="search",
            description="Search for information on the internet"
        )
    
    async def execute(self, query: str, **kwargs) -> str:
        """Execute search"""
        # Placeholder implementation
        return f"Search results for: {query}"
    
    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"]["query"] = {
            "type": "string",
            "description": "Search query"
        }
        return schema


class CalculatorTool(Tool):
    """Tool for mathematical calculations"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations"
        )
    
    async def execute(self, expression: str, **kwargs) -> str:
        """Execute calculation"""
        try:
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"]["expression"] = {
            "type": "string",
            "description": "Mathematical expression to evaluate"
        }
        return schema


class CodeExecutionTool(Tool):
    """Tool for code execution"""
    
    def __init__(self):
        super().__init__(
            name="execute_code",
            description="Execute Python code snippets"
        )
    
    async def execute(self, code: str, **kwargs) -> str:
        """Execute code"""
        try:
            # Note: This is a simplified implementation
            # In production, use sandboxed execution
            result = eval(code)
            return str(result)
        except Exception as e:
            return f"Code execution error: {str(e)}"
    
    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"]["code"] = {
            "type": "string",
            "description": "Python code to execute"
        }
        return schema


class FileTool(Tool):
    """Tool for file operations"""
    
    def __init__(self):
        super().__init__(
            name="file_operations",
            description="Read and write files"
        )
    
    async def execute(self, operation: str, path: str, content: Optional[str] = None, **kwargs) -> str:
        """Execute file operation"""
        try:
            if operation == "read":
                with open(path, 'r') as f:
                    return f.read()
            elif operation == "write":
                with open(path, 'w') as f:
                    f.write(content or "")
                return f"File written to {path}"
            else:
                return "Unknown operation"
        except Exception as e:
            return f"File operation error: {str(e)}"
    
    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"]["operation"] = {
            "type": "string",
            "enum": ["read", "write"],
            "description": "File operation to perform"
        }
        schema["parameters"]["properties"]["path"] = {
            "type": "string",
            "description": "File path"
        }
        schema["parameters"]["properties"]["content"] = {
            "type": "string",
            "description": "Content to write (for write operation)"
        }
        return schema
