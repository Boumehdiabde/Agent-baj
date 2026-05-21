"""Memory management module"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime


class Message:
    """Represents a single message in memory"""
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        self.role = role  # "user", "assistant", "system"
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, str]:
        """Convert message to dictionary format"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


class Memory(ABC):
    """Abstract base class for memory systems"""
    
    @abstractmethod
    def add(self, role: str, content: str) -> None:
        """Add message to memory"""
        pass
    
    @abstractmethod
    def retrieve(self, limit: int = 10) -> List[Message]:
        """Retrieve messages from memory"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all memory"""
        pass
    
    @abstractmethod
    def get_context(self) -> str:
        """Get formatted context from memory"""
        pass


class ConversationMemory(Memory):
    """In-memory conversation history storage"""
    
    def __init__(self, max_messages: int = 100, context_window: int = 4096):
        self.max_messages = max_messages
        self.context_window = context_window
        self.messages: List[Message] = []
    
    def add(self, role: str, content: str) -> None:
        """Add message to conversation history"""
        message = Message(role, content)
        self.messages.append(message)
        
        # Maintain max message limit
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def retrieve(self, limit: int = 10) -> List[Message]:
        """Retrieve last N messages"""
        return self.messages[-limit:] if self.messages else []
    
    def clear(self) -> None:
        """Clear all conversation history"""
        self.messages.clear()
    
    def get_context(self) -> str:
        """Get formatted conversation context"""
        context = ""
        for msg in self.retrieve(limit=20):
            context += f"{msg.role.upper()}: {msg.content}\n"
        return context
    
    def get_message_count(self) -> int:
        """Get total number of messages in memory"""
        return len(self.messages)
    
    def get_conversation_length(self) -> int:
        """Get approximate character count of all messages"""
        return sum(len(msg.content) for msg in self.messages)
    
    def get_messages_as_dicts(self) -> List[Dict[str, str]]:
        """Get all messages as dictionaries for LLM APIs"""
        return [msg.to_dict() for msg in self.messages]


class SummaryMemory(Memory):
    """Memory with conversation summarization"""
    
    def __init__(self, max_messages: int = 50, summarize_at: int = 30):
        self.max_messages = max_messages
        self.summarize_at = summarize_at
        self.messages: List[Message] = []
        self.summary = ""
    
    def add(self, role: str, content: str) -> None:
        """Add message and trigger summarization if needed"""
        message = Message(role, content)
        self.messages.append(message)
        
        if len(self.messages) > self.summarize_at:
            self._summarize()
    
    def _summarize(self) -> None:
        """Summarize older messages"""
        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def retrieve(self, limit: int = 10) -> List[Message]:
        """Retrieve last N messages"""
        return self.messages[-limit:] if self.messages else []
    
    def clear(self) -> None:
        """Clear all memory"""
        self.messages.clear()
        self.summary = ""
    
    def get_context(self) -> str:
        """Get context including summary"""
        context = ""
        if self.summary:
            context += f"SUMMARY:\n{self.summary}\n\n"
        
        context += "RECENT MESSAGES:\n"
        for msg in self.retrieve(limit=10):
            context += f"{msg.role.upper()}: {msg.content}\n"
        return context


class EntityMemory(Memory):
    """Memory that tracks entities and facts"""
    
    def __init__(self):
        self.messages: List[Message] = []
        self.entities: Dict[str, Any] = {}
        self.facts: List[str] = []
    
    def add(self, role: str, content: str) -> None:
        """Add message and extract entities"""
        message = Message(role, content)
        self.messages.append(message)
        self._extract_entities(content)
    
    def _extract_entities(self, content: str) -> None:
        """Extract entities from content (basic implementation)"""
        # This is a placeholder for entity extraction
        # In production, use NER models
        pass
    
    def add_entity(self, name: str, value: Any) -> None:
        """Add or update an entity"""
        self.entities[name] = value
    
    def add_fact(self, fact: str) -> None:
        """Add a fact to memory"""
        if fact not in self.facts:
            self.facts.append(fact)
    
    def retrieve(self, limit: int = 10) -> List[Message]:
        """Retrieve messages"""
        return self.messages[-limit:] if self.messages else []
    
    def clear(self) -> None:
        """Clear all memory"""
        self.messages.clear()
        self.entities.clear()
        self.facts.clear()
    
    def get_context(self) -> str:
        """Get context with entities and facts"""
        context = ""
        
        if self.entities:
            context += "KNOWN ENTITIES:\n"
            for key, value in self.entities.items():
                context += f"- {key}: {value}\n"
            context += "\n"
        
        if self.facts:
            context += "KNOWN FACTS:\n"
            for fact in self.facts:
                context += f"- {fact}\n"
            context += "\n"
        
        context += "MESSAGE HISTORY:\n"
        for msg in self.retrieve(limit=10):
            context += f"{msg.role.upper()}: {msg.content}\n"
        
        return context
