"""Unit tests for agent system"""
import pytest
from core.memory import ConversationMemory, Message
from core.router import AgentRouter


@pytest.fixture
def memory():
    """Fixture for conversation memory"""
    return ConversationMemory()


@pytest.fixture
def router():
    """Fixture for agent router"""
    return AgentRouter()


def test_message_creation():
    """Test message creation"""
    msg = Message("user", "Hello, world!")
    assert msg.role == "user"
    assert msg.content == "Hello, world!"
    assert msg.timestamp is not None


def test_message_to_dict():
    """Test message to dictionary conversion"""
    msg = Message("user", "Test message")
    msg_dict = msg.to_dict()
    assert msg_dict["role"] == "user"
    assert msg_dict["content"] == "Test message"
    assert "timestamp" in msg_dict


def test_conversation_memory_add(memory):
    """Test adding messages to memory"""
    memory.add("user", "First message")
    memory.add("assistant", "Response")
    assert memory.get_message_count() == 2


def test_conversation_memory_retrieve(memory):
    """Test retrieving messages from memory"""
    memory.add("user", "Message 1")
    memory.add("assistant", "Response 1")
    memory.add("user", "Message 2")
    
    messages = memory.retrieve(limit=2)
    assert len(messages) == 2
    assert messages[-1].content == "Message 2"


def test_conversation_memory_clear(memory):
    """Test clearing memory"""
    memory.add("user", "Test")
    memory.clear()
    assert memory.get_message_count() == 0


def test_router_analyze_task(router):
    """Test task analysis"""
    agent_type = router.analyze_task("Write a Python function")
    assert agent_type == "coding"
    
    agent_type = router.analyze_task("Research machine learning trends")
    assert agent_type == "research"


def test_router_route_task(router):
    """Test task routing"""
    result = router.route_task("Create an automation workflow")
    assert result["agent_type"] == "automation"
    assert result["task"] == "Create an automation workflow"
    assert "context" in result


def test_router_get_agent_description(router):
    """Test getting agent description"""
    desc = router.get_agent_description("research")
    assert "research" in desc.lower()


def test_router_stats(router):
    """Test router statistics"""
    stats = router.get_routing_stats()
    assert "total_messages" in stats
    assert "conversation_length" in stats
    assert "available_agents" in stats
    assert len(stats["available_agents"]) == 4
