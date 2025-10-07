# src/memory/working_memory.py
from collections import deque
from typing import List, Dict, Any, Optional
from datetime import datetime


class WorkingMemory:
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.messages = deque(maxlen=max_size)

    def add_message(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a message to working memory"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        self.messages.append(message)

    def get_recent(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent messages"""
        if n is None:
            return list(self.messages)
        return list(self.messages)[-n:]

    def clear(self):
        """Clear working memory"""
        self.messages.clear()

    def get_context_string(self) -> str:
        """Get formatted context string for LLM"""
        context_parts = []
        for msg in self.messages:
            context_parts.append(f"{msg['role']}: {msg['content']}")
        return "\n".join(context_parts)

    def __len__(self):
        return len(self.messages)
