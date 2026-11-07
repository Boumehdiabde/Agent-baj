"""Security-focused regression tests for built-in tools."""
import pytest

from core.tools import CalculatorTool, CodeExecutionTool, FileTool


@pytest.mark.asyncio
async def test_calculator_accepts_arithmetic():
    assert await CalculatorTool().execute(expression="(2 + 3) * 4") == "20"


@pytest.mark.asyncio
async def test_calculator_rejects_python_execution():
    with pytest.raises(ValueError):
        await CalculatorTool().execute(expression="__import__('os').getcwd()")


@pytest.mark.asyncio
async def test_code_execution_is_disabled():
    with pytest.raises(NotImplementedError):
        await CodeExecutionTool().execute(code="1 + 1")


@pytest.mark.asyncio
async def test_file_tool_rejects_workspace_escape(tmp_path):
    tool = FileTool(str(tmp_path / "workspace"))
    with pytest.raises(ValueError):
        await tool.execute(operation="write", path="../outside.txt", content="blocked")


@pytest.mark.asyncio
async def test_file_tool_can_write_inside_workspace(tmp_path):
    tool = FileTool(str(tmp_path / "workspace"))
    assert await tool.execute(operation="write", path="nested/note.txt", content="hello") == "File written to nested/note.txt"
    assert await tool.execute(operation="read", path="nested/note.txt") == "hello"
