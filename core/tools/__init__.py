"""Tools system for agents."""
import ast
import operator
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional


class Tool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        pass

    def get_schema(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description, "parameters": {"type": "object", "properties": {}}}


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        self.tools.pop(name, None)

    def get(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    async def execute(self, name: str, **kwargs) -> str:
        tool = self.get(name)
        if tool is None:
            raise ValueError(f"Tool '{name}' not found")
        return await tool.execute(**kwargs)

    def list_tools(self) -> List[str]:
        return list(self.tools)

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        return [tool.get_schema() for tool in self.tools.values()]


class SearchTool(Tool):
    def __init__(self):
        super().__init__("search", "Search for information on the internet (not configured)")

    async def execute(self, query: str, **kwargs) -> str:
        raise NotImplementedError("Search provider is not configured")

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"]["query"] = {"type": "string", "description": "Search query"}
        schema["parameters"]["required"] = ["query"]
        return schema


class CalculatorTool(Tool):
    """Evaluate arithmetic expressions without Python code execution."""

    _binary_ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                   ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
                   ast.Mod: operator.mod, ast.Pow: operator.pow}
    _unary_ops = {ast.UAdd: operator.pos, ast.USub: operator.neg}

    def __init__(self):
        super().__init__("calculator", "Safely evaluate a basic arithmetic expression")

    @classmethod
    def _evaluate(cls, node):
        if isinstance(node, ast.Expression):
            return cls._evaluate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in cls._binary_ops:
            left, right = cls._evaluate(node.left), cls._evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("Exponent is too large")
            value = cls._binary_ops[type(node.op)](left, right)
            if isinstance(value, (int, float)) and abs(value) > 1e100:
                raise ValueError("Result is too large")
            return value
        if isinstance(node, ast.UnaryOp) and type(node.op) in cls._unary_ops:
            return cls._unary_ops[type(node.op)](cls._evaluate(node.operand))
        raise ValueError("Only basic arithmetic is allowed")

    async def execute(self, expression: str, **kwargs) -> str:
        try:
            tree = ast.parse(expression, mode="eval")
            return str(self._evaluate(tree))
        except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
            raise ValueError(f"Invalid arithmetic expression: {exc}") from exc

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"]["expression"] = {"type": "string", "description": "Arithmetic expression"}
        schema["parameters"]["required"] = ["expression"]
        return schema


class CodeExecutionTool(Tool):
    """Execution is intentionally disabled; arbitrary code needs an isolated sandbox."""

    def __init__(self):
        super().__init__("execute_code", "Disabled: arbitrary code execution requires a dedicated sandbox")

    async def execute(self, code: str, **kwargs) -> str:
        raise NotImplementedError("Code execution is disabled because this service has no secure sandbox")

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"]["code"] = {"type": "string", "description": "Not executable in this service"}
        schema["parameters"]["required"] = ["code"]
        return schema


class FileTool(Tool):
    """Read/write files under a designated workspace only."""

    def __init__(self, workspace: Optional[str] = None):
        super().__init__("file_operations", "Read and write files under the configured workspace")
        self.workspace = Path(workspace or "workspace").resolve()

    def _safe_path(self, path: str) -> Path:
        candidate = (self.workspace / path).resolve()
        if not candidate.is_relative_to(self.workspace):
            raise ValueError("Path must remain inside the workspace")
        return candidate

    async def execute(self, operation: str, path: str, content: Optional[str] = None, **kwargs) -> str:
        target = self._safe_path(path)
        if operation == "read":
            if not target.is_file():
                raise FileNotFoundError("File does not exist in workspace")
            return target.read_text(encoding="utf-8")
        if operation == "write":
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content or "", encoding="utf-8")
            return f"File written to {path}"
        raise ValueError("Operation must be 'read' or 'write'")

    def get_schema(self) -> Dict[str, Any]:
        schema = super().get_schema()
        schema["parameters"]["properties"].update({
            "operation": {"type": "string", "enum": ["read", "write"]},
            "path": {"type": "string", "description": "Path relative to workspace"},
            "content": {"type": "string", "description": "Content for write operation"},
        })
        schema["parameters"]["required"] = ["operation", "path"]
        return schema
