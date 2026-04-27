"""Tests for model clients."""

import pytest

from long_horizon_bench.models import (
    ChatResponse,
    DeepSeekClient,
    GLMClient,
    KimiClient,
    Message,
    MockModelClient,
    ModelConfig,
    Usage,
)


class TestMessage:
    """Test Message dataclass."""

    def test_message_creation(self) -> None:
        """Test creating a message."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.tool_calls is None

    def test_message_with_tool_calls(self) -> None:
        """Test message with tool calls."""
        tool_calls = [{"id": "call_1", "function": {"name": "test"}}]
        msg = Message(role="assistant", content=None, tool_calls=tool_calls)
        assert msg.role == "assistant"
        assert msg.content is None
        assert msg.tool_calls == tool_calls


class TestUsage:
    """Test Usage dataclass."""

    def test_usage_defaults(self) -> None:
        """Test usage with defaults."""
        usage = Usage()
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0

    def test_usage_with_values(self) -> None:
        """Test usage with values."""
        usage = Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 20
        assert usage.total_tokens == 30


class TestMockModelClient:
    """Test MockModelClient."""

    @pytest.fixture
    def mock_client(self) -> MockModelClient:
        """Create a mock client."""
        return MockModelClient()

    @pytest.mark.asyncio
    async def test_chat_basic(self, mock_client: MockModelClient) -> None:
        """Test basic chat completion."""
        messages = [Message(role="user", content="Hello")]
        response = await mock_client.chat(messages)
        
        assert isinstance(response, ChatResponse)
        assert response.message.role == "assistant"
        assert response.message.content is not None
        assert "Mock response" in response.message.content
        assert response.usage.total_tokens > 0
        assert response.cost_usd == 0.0
        assert response.latency_ms >= 0

    @pytest.mark.asyncio
    async def test_chat_with_tools(self, mock_client: MockModelClient) -> None:
        """Test chat with tools."""
        messages = [Message(role="user", content="Search for something")]
        tools = [{"type": "function", "function": {"name": "search"}}]
        
        for _ in range(3):
            response = await mock_client.chat(messages, tools=tools)
        
        assert response.message.tool_calls is not None
        assert len(response.message.tool_calls) > 0

    @pytest.mark.asyncio
    async def test_chat_stream(self, mock_client: MockModelClient) -> None:
        """Test streaming chat."""
        messages = [Message(role="user", content="Hello")]
        chunks = []
        async for chunk in mock_client.chat_stream(messages):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)

    def test_count_tokens(self, mock_client: MockModelClient) -> None:
        """Test token counting."""
        messages = [Message(role="user", content="Hello world")]
        count = mock_client.count_tokens(messages)
        assert count > 0

    def test_count_tokens_with_tools(self, mock_client: MockModelClient) -> None:
        """Test token counting with tools."""
        messages = [Message(role="user", content="Hello")]
        tools = [{"type": "function", "function": {"name": "test"}}]
        count = mock_client.count_tokens(messages, tools)
        assert count > len("Hello") // 4

    def test_estimate_cost(self, mock_client: MockModelClient) -> None:
        """Test cost estimation."""
        cost = mock_client.estimate_cost(100, 50)
        assert cost == 0.0

    def test_get_stats(self, mock_client: MockModelClient) -> None:
        """Test getting stats."""
        stats = mock_client.get_stats()
        assert "total_calls" in stats
        assert "total_tokens" in stats
        assert "total_cost_usd" in stats

    @pytest.mark.asyncio
    async def test_stats_update(self, mock_client: MockModelClient) -> None:
        """Test stats are updated after chat."""
        initial_stats = mock_client.get_stats()
        
        messages = [Message(role="user", content="Hello")]
        await mock_client.chat(messages)
        
        updated_stats = mock_client.get_stats()
        assert updated_stats["total_calls"] == initial_stats["total_calls"] + 1
        assert updated_stats["total_tokens"] > initial_stats["total_tokens"]


class TestGLMClient:
    """Test GLMClient initialization."""

    def test_client_creation(self) -> None:
        """Test creating GLM client."""
        config = ModelConfig(
            api_key="test_key",
            base_url="https://test.com",
            model="glm-5.1",
        )
        client = GLMClient(config)
        assert client.config == config

    def test_estimate_cost(self) -> None:
        """Test GLM cost estimation."""
        config = ModelConfig(api_key="test", base_url="test", model="test")
        client = GLMClient(config)
        cost = client.estimate_cost(1000, 1000)
        expected = 0.003 + 0.006
        assert abs(cost - expected) < 0.0001


class TestKimiClient:
    """Test KimiClient initialization."""

    def test_client_creation(self) -> None:
        """Test creating Kimi client."""
        config = ModelConfig(
            api_key="test_key",
            base_url="https://test.com",
            model="kimi-k2-6",
        )
        client = KimiClient(config)
        assert client.config == config

    def test_estimate_cost(self) -> None:
        """Test Kimi cost estimation."""
        config = ModelConfig(api_key="test", base_url="test", model="test")
        client = KimiClient(config)
        cost = client.estimate_cost(1000, 1000)
        expected = 0.005 + 0.015
        assert abs(cost - expected) < 0.0001


class TestDeepSeekClient:
    """Test DeepSeekClient initialization."""

    def test_client_creation(self) -> None:
        """Test creating DeepSeek client."""
        config = ModelConfig(
            api_key="test_key",
            base_url="https://test.com",
            model="deepseek-v4-pro",
        )
        client = DeepSeekClient(config)
        assert client.config == config

    def test_estimate_cost(self) -> None:
        """Test DeepSeek cost estimation."""
        config = ModelConfig(api_key="test", base_url="test", model="test")
        client = DeepSeekClient(config)
        cost = client.estimate_cost(1000, 1000)
        expected = 0.002 + 0.008
        assert abs(cost - expected) < 0.0001


class TestModelConfig:
    """Test ModelConfig dataclass."""

    def test_config_defaults(self) -> None:
        """Test config with defaults."""
        config = ModelConfig(
            api_key="test",
            base_url="https://test.com",
            model="test-model",
        )
        assert config.api_key == "test"
        assert config.base_url == "https://test.com"
        assert config.model == "test-model"
        assert config.timeout_seconds == 60.0
        assert config.max_retries == 3
        assert config.temperature == 0.7
        assert config.max_tokens is None

    def test_config_custom(self) -> None:
        """Test config with custom values."""
        config = ModelConfig(
            api_key="test",
            base_url="https://test.com",
            model="test-model",
            timeout_seconds=120.0,
            max_retries=5,
            temperature=0.5,
            max_tokens=1000,
        )
        assert config.timeout_seconds == 120.0
        assert config.max_retries == 5
        assert config.temperature == 0.5
        assert config.max_tokens == 1000
