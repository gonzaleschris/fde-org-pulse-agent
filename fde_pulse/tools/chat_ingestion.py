"""Chat Ingestion Tool with PII Sanitization, Token Estimation & Parameter Validation."""
import json
import re
from typing import List, Dict, Any, Union, Optional
from pathlib import Path
from ..models.schemas import ChatMessage, ChatIngestionBatch
from ..config import TARGET_CHAT_GROUP

class ChatIngestionTool:
    """Ingests, cleans, and sanitizes group chat communications from Google Chat."""

    def __init__(self, target_channel: str = TARGET_CHAT_GROUP):
        self.target_channel = target_channel

    def sanitize_content(self, text: str) -> str:
        """Sanitizes sensitive tokens, credentials, and API keys from raw chat logs.
        
        Args:
            text: Raw message text string.

        Returns:
            Sanitized string with sensitive keys replaced by tokens.
        """
        # Redact Google Cloud / Vertex API keys
        text = re.sub(r'(AIza[0-9A-Za-z\-_]{15,45})', '[REDACTED_API_KEY]', text)
        # Redact Bearer / OAuth Tokens
        text = re.sub(r'(Bearer\s+[A-Za-z0-9\-_\.]+)', '[REDACTED_TOKEN]', text)
        # Redact generic private keys
        text = re.sub(r'(sk-[a-zA-Z0-9\-_]{15,})', '[REDACTED_SECRET]', text)
        return text

    def estimate_tokens(self, messages: List[ChatMessage]) -> int:
        """Estimates token footprint (~4 characters per token).
        
        Args:
            messages: List of ChatMessage instances.

        Returns:
            Integer estimated token count.
        """
        total_chars = sum(len(m.content) for m in messages)
        return max(1, total_chars // 4)

    def ingest_from_file(self, file_path: Union[str, Path], week_identifier: str = "2026-W36") -> ChatIngestionBatch:
        """Ingests chat logs from JSON file and returns a validated batch.
        
        Args:
            file_path: Filesystem path to JSON chat export.
            week_identifier: ISO week format (e.g. 2026-W36).

        Returns:
            Validated ChatIngestionBatch container.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Chat data file not found at {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        raw_messages = raw_data if isinstance(raw_data, list) else raw_data.get("messages", [])
        
        parsed_messages: List[ChatMessage] = []
        senders = set()

        for idx, item in enumerate(raw_messages):
            msg_id = item.get("id", f"msg_{idx+1}")
            sender = item.get("sender", "Unknown Engineer")
            role = item.get("role", "FDE Engineer")
            timestamp = item.get("timestamp", "2026-09-01T00:00:00Z")
            channel = item.get("channel", self.target_channel)
            raw_content = item.get("content", "")
            reactions = item.get("reactions_count", 0)
            threads = item.get("thread_replies_count", 0)

            clean_content = self.sanitize_content(raw_content)
            
            message = ChatMessage(
                id=msg_id,
                sender=sender,
                role=role,
                timestamp=timestamp,
                content=clean_content,
                reactions_count=reactions,
                thread_replies_count=threads,
                channel=channel
            )
            parsed_messages.append(message)
            senders.add(sender)

        tokens = self.estimate_tokens(parsed_messages)

        return ChatIngestionBatch(
            week_identifier=week_identifier,
            total_messages=len(parsed_messages),
            active_contributors=len(senders),
            messages=parsed_messages,
            estimated_tokens=tokens
        )
