# src/memory/session_memory.py
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.knowledge_base.cache import CacheStore
from loguru import logger


class SessionMemory:
    """Session-based memory management"""

    def __init__(self, session_id: str, max_messages: int = 50):
        self.session_id = session_id
        self.max_messages = max_messages
        self.cache = CacheStore()
        self.session_key = f"session:{session_id}"

    def add_interaction(
        self,
        user_message: str,
        assistant_response: str,
        metadata: Dict[str, Any] = None,
    ):
        """Add user-assistant interaction to session"""
        interaction = {
            "user_message": user_message,
            "assistant_response": assistant_response,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        # Get existing session data
        session_data = self.cache.get(self.session_key) or {
            "interactions": [],
            "created_at": datetime.utcnow().isoformat(),
        }

        # Add new interaction
        session_data["interactions"].append(interaction)

        # Keep only recent interactions
        if len(session_data["interactions"]) > self.max_messages:
            session_data["interactions"] = session_data["interactions"][
                -self.max_messages :
            ]

        # Update cache (expire in 24 hours)
        self.cache.set(self.session_key, session_data, expire=86400)

        logger.info(f"Added interaction to session {self.session_id}")

    def get_conversation_history(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history"""
        session_data = self.cache.get(self.session_key)

        if not session_data:
            return []

        interactions = session_data.get("interactions", [])

        if limit:
            interactions = interactions[-limit:]

        return interactions

    def get_context_string(self, limit: int = 10) -> str:
        """Get formatted context for LLM"""
        interactions = self.get_conversation_history(limit)

        context_parts = []
        for interaction in interactions:
            context_parts.append(f"User: {interaction['user_message']}")
            context_parts.append(f"Assistant: {interaction['assistant_response']}")

        return "\n".join(context_parts)

    def clear_session(self):
        """Clear session memory"""
        self.cache.delete(self.session_key)
        logger.info(f"Cleared session {self.session_id}")

    def get_session_metadata(self) -> Dict[str, Any]:
        """Get session metadata"""
        session_data = self.cache.get(self.session_key)

        if not session_data:
            return {}

        interactions = session_data.get("interactions", [])

        return {
            "session_id": self.session_id,
            "created_at": session_data.get("created_at"),
            "interaction_count": len(interactions),
            "last_interaction": interactions[-1]["timestamp"] if interactions else None,
        }
