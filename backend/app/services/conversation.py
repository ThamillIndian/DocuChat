"""
Conversation memory and prompt chaining system
"""
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ChatMessage:
    role: str  # "user" or "assistant"
    content: str
    timestamp: float
    sources: Optional[List[Dict]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "sources": self.sources or []
        }

class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: List[ChatMessage] = []
        self.session_start = time.time()
    
    def add_message(self, role: str, content: str, sources: Optional[List[Dict]] = None):
        """Add a message to conversation history"""
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=time.time(),
            sources=sources
        )
        self.messages.append(message)
        
        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_conversation_context(self, max_chars: int = 4000) -> str:
        """Get formatted conversation history for context"""
        if not self.messages:
            return ""
        
        context_parts = []
        current_chars = 0
        
        # Start from most recent messages and work backwards
        for message in reversed(self.messages[-10:]):  # Last 10 messages
            formatted_msg = f"{message.role.title()}: {message.content}"
            
            if current_chars + len(formatted_msg) > max_chars:
                break
                
            context_parts.insert(0, formatted_msg)
            current_chars += len(formatted_msg)
        
        return "\n".join(context_parts)
    
    def get_recent_context(self, last_n: int = 5) -> str:
        """Get recent conversation context"""
        recent_messages = self.messages[-last_n:] if len(self.messages) > last_n else self.messages
        
        context_parts = []
        for msg in recent_messages:
            context_parts.append(f"{msg.role.title()}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear conversation history"""
        self.messages.clear()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        return {
            "total_messages": len(self.messages),
            "user_messages": len([m for m in self.messages if m.role == "user"]),
            "assistant_messages": len([m for m in self.messages if m.role == "assistant"]),
            "session_duration": time.time() - self.session_start,
            "last_message_time": self.messages[-1].timestamp if self.messages else None
        }

class ConversationManager:
    """Manages multiple conversation sessions"""
    
    def __init__(self):
        self.conversations: Dict[str, ConversationMemory] = {}
    
    def get_conversation(self, session_id: str) -> ConversationMemory:
        """Get or create conversation for session"""
        if session_id not in self.conversations:
            self.conversations[session_id] = ConversationMemory()
        return self.conversations[session_id]
    
    def clear_conversation(self, session_id: str):
        """Clear conversation for session"""
        if session_id in self.conversations:
            self.conversations[session_id].clear()
    
    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Clean up old conversations"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        to_remove = []
        for session_id, conversation in self.conversations.items():
            if current_time - conversation.session_start > max_age_seconds:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.conversations[session_id]

# Global conversation manager
conversation_manager = ConversationManager()


