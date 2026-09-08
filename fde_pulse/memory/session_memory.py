"""Async Session Memory Manager with History Compaction and Persistent State."""
import asyncio
import sqlite3
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..models.schemas import SessionState, ConversationTurn
from ..config import MAX_HISTORY_TOKENS, COMPACTED_SUMMARY_TARGET

logger = logging.getLogger("fde_pulse.memory")

SYSTEM_INSTRUCTION = """You are the Google Cloud FDE Org Pulse & Weekly Intelligence Agent.
Your mission is to autonomously analyze internal communications from the 'AI GTM Tech - All Team' chat group,
extracting high-signal technological patterns, celebrating customer wins, surfacing P0/P1 operational risks,
and formulating strategic, actionable recommendations for Forward Deployed Engineering (FDE) leadership.
Maintain an objective, structured, and action-oriented tone. Strictly enforce security perimeters, PII redaction,
and schema validation across all tool outputs."""

class AsyncSessionMemory:
    """Manages persistent conversational session history with async operations and automatic context compaction."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = str(db_path)
        self._shared_conn = sqlite3.connect("file:mem_session?mode=memory&cache=shared", uri=True, check_same_thread=False) if db_path == ":memory:" else None
        self._init_db()

    def _get_connection(self):
        if self._shared_conn is not None:
            return self._shared_conn
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=MEMORY")
        return conn

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT,
                updated_at TEXT,
                system_instruction TEXT,
                compacted_summary TEXT,
                total_token_count INTEGER,
                raw_json TEXT
            )
        """)
        conn.commit()
        if self._shared_conn is None:
            conn.close()

    async def get_or_create_session(self, session_id: str) -> SessionState:
        """Asynchronously retrieves an existing session or initializes a new one."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_get_or_create, session_id)

    def _sync_get_or_create(self, session_id: str) -> SessionState:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT raw_json FROM conversation_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if row:
            if self._shared_conn is None:
                conn.close()
            return SessionState.model_validate_json(row[0])
        
        # Create fresh session
        new_session = SessionState(
            session_id=session_id,
            system_instruction=SYSTEM_INSTRUCTION,
            turns=[],
            total_token_count=0
        )
        cursor.execute("""
            INSERT INTO conversation_sessions 
            (session_id, created_at, updated_at, system_instruction, compacted_summary, total_token_count, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            new_session.session_id,
            new_session.created_at,
            new_session.updated_at,
            new_session.system_instruction,
            new_session.compacted_summary,
            new_session.total_token_count,
            new_session.model_dump_json()
        ))
        conn.commit()
        if self._shared_conn is None:
            conn.close()
        return new_session

    async def append_turn(self, session_id: str, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None) -> SessionState:
        """Asynchronously adds a turn to the session history and triggers compaction if token ceiling is reached."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_append_turn, session_id, role, content, tool_calls)

    def _sync_append_turn(self, session_id: str, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None) -> SessionState:
        session = self._sync_get_or_create(session_id)
        
        turn_id = f"turn_{len(session.turns) + 1}_{datetime.utcnow().strftime('%H%M%S')}"
        turn_tokens = len(content) // 4
        
        turn = ConversationTurn(
            turn_id=turn_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            token_count=turn_tokens
        )
        session.turns.append(turn)
        session.total_token_count += turn_tokens
        session.updated_at = datetime.utcnow().isoformat()

        # Automatic Context Compaction
        if session.total_token_count > MAX_HISTORY_TOKENS:
            self._compact_history(session)

        # Persist update
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE conversation_sessions 
            SET updated_at = ?, compacted_summary = ?, total_token_count = ?, raw_json = ?
            WHERE session_id = ?
        """, (
            session.updated_at,
            session.compacted_summary,
            session.total_token_count,
            session.model_dump_json(),
            session.session_id
        ))
        conn.commit()
        if self._shared_conn is None:
            conn.close()

        return session

    def _compact_history(self, session: SessionState):
        """Compacts older turns into a rolling executive summary to maintain context within token bounds."""
        logger.info(f"Triggering context compaction for session {session.session_id} (Tokens: {session.total_token_count} > {MAX_HISTORY_TOKENS})")
        
        turns_to_compact = session.turns[:-4]  # Keep the 4 most recent turns active
        retained_turns = session.turns[-4:]

        summary_snippets = []
        for t in turns_to_compact:
            summary_snippets.append(f"[{t.role.upper()}]: {t.content[:150]}...")

        existing_summary = session.compacted_summary or ""
        new_summary = f"{existing_summary}\n\n[Compacted History Summary]:\n" + "\n".join(summary_snippets)
        
        session.compacted_summary = new_summary[:COMPACTED_SUMMARY_TARGET * 4]
        session.turns = retained_turns
        session.total_token_count = sum(t.token_count for t in retained_turns) + (len(session.compacted_summary) // 4)
