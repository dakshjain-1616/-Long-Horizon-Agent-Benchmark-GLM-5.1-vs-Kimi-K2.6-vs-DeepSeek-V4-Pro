"""Tests for tools."""


import pytest

from long_horizon_bench.tools import (
    CodeSearchTool,
    FileEditTool,
    ShellExecTool,
    ToolResult,
    WebSearchTool,
)


class TestToolResult:
    def test_result_creation(self) -> None:
        result = ToolResult(success=True, output="test output")
        assert result.success is True
        assert result.output == "test output"
        assert result.error is None

    def test_result_with_error(self) -> None:
        result = ToolResult(success=False, output="", error="test error")
        assert result.success is False
        assert result.error == "test error"


class TestFileEditTool:
    @pytest.mark.asyncio
    async def test_mock_read(self) -> None:
        tool = FileEditTool(mock_mode=True)
        result = await tool.execute(operation="read", path="/test/file.txt")
        assert result.success is True
        assert "MOCK" in result.output

    @pytest.mark.asyncio
    async def test_real_write_and_read(self, tmp_path) -> None:
        tool = FileEditTool(mock_mode=False)
        test_file = tmp_path / "test.txt"
        write_result = await tool.execute(operation="write", path=str(test_file), content="Hello World")
        assert write_result.success is True
        assert test_file.exists()
        read_result = await tool.execute(operation="read", path=str(test_file))
        assert read_result.success is True
        assert "Hello World" in read_result.output

    @pytest.mark.asyncio
    async def test_real_edit(self, tmp_path) -> None:
        tool = FileEditTool(mock_mode=False)
        test_file = tmp_path / "test.txt"
        await tool.execute(operation="write", path=str(test_file), content="Hello World")
        edit_result = await tool.execute(operation="edit", path=str(test_file), old_string="World", new_string="Universe")
        assert edit_result.success is True
        content = test_file.read_text()
        assert "Hello Universe" in content


class TestWebSearchTool:
    @pytest.mark.asyncio
    async def test_mock_search(self) -> None:
        tool = WebSearchTool(mock_mode=True)
        result = await tool.execute(query="python programming", num_results=3)
        assert result.success is True
        assert "MOCK" in result.output or "python programming" in result.output

    def test_get_schema(self) -> None:
        tool = WebSearchTool(mock_mode=True)
        schema = tool.get_schema()
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "web_search"


class TestShellExecTool:
    @pytest.mark.asyncio
    async def test_mock_exec(self) -> None:
        tool = ShellExecTool(mock_mode=True)
        result = await tool.execute(command="ls -la")
        assert result.success is True
        assert "MOCK" in result.output

    @pytest.mark.asyncio
    async def test_real_allowed_command(self) -> None:
        tool = ShellExecTool(mock_mode=False)
        result = await tool.execute(command="echo hello")
        assert result.success is True
        assert "hello" in result.output

    @pytest.mark.asyncio
    async def test_disallowed_command(self) -> None:
        tool = ShellExecTool(mock_mode=False, allowed_commands=["echo"])
        result = await tool.execute(command="cat /etc/passwd")
        assert result.success is False
        assert "not in allowed commands" in result.error


class TestCodeSearchTool:
    @pytest.mark.asyncio
    async def test_mock_search(self) -> None:
        tool = CodeSearchTool(mock_mode=True)
        result = await tool.execute(pattern="def test", path=".", max_results=5)
        assert result.success is True
        assert "MOCK" in result.output

    @pytest.mark.asyncio
    async def test_real_search(self, tmp_path) -> None:
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")
        tool = CodeSearchTool(mock_mode=False)
        result = await tool.execute(pattern="def hello", path=str(tmp_path), file_pattern="*.py")
        assert result.success is True
        assert "def hello" in result.output
