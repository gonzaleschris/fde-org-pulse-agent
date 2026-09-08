"""Data models, JSON schemas, and structured constraints (Standard Python + Pydantic compatible)."""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json

# Try importing Pydantic; if not present, provide lightweight fallback
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    class BaseModel:
        def to_dict(self) -> Dict[str, Any]:
            return asdict(self)
        def model_dump(self) -> Dict[str, Any]:
            return asdict(self)
        def model_dump_json(self, indent: Optional[int] = None) -> str:
            return json.dumps(asdict(self), indent=indent)
        @classmethod
        def model_validate(cls, data: Dict[str, Any]):
            return cls(**data)
        @classmethod
        def model_validate_json(cls, json_str: str):
            return cls(**json.loads(json_str))
    def Field(default=..., **kwargs):
        return default

@dataclass
class ChatMessage:
    id: str
    sender: str
    timestamp: str
    content: str
    role: Optional[str] = "FDE Engineer"
    reactions_count: int = 0
    thread_replies_count: int = 0
    channel: str = "AI GTM Tech - All Team"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ChatIngestionBatch:
    week_identifier: str
    total_messages: int
    active_contributors: int
    messages: List[ChatMessage] = field(default_factory=list)
    estimated_tokens: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "week_identifier": self.week_identifier,
            "total_messages": self.total_messages,
            "active_contributors": self.active_contributors,
            "messages": [m.to_dict() for m in self.messages],
            "estimated_tokens": self.estimated_tokens
        }

@dataclass
class HotTopic:
    title: str
    category: str
    mentions_count: int
    summary: str
    impact_level: str = "High"
    key_contributors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def model_validate(cls, data: Dict[str, Any]):
        return cls(**data)

@dataclass
class PositiveWin:
    headline: str
    customer_or_project: str
    description: str
    lead_engineers: List[str] = field(default_factory=list)
    impact_metrics: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def model_validate(cls, data: Dict[str, Any]):
        return cls(**data)

@dataclass
class LeadershipRisk:
    risk_id: str
    severity: str
    headline: str
    friction_area: str
    symptoms: str
    suggested_mitigation: str
    affected_teams_or_customers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def model_validate(cls, data: Dict[str, Any]):
        return cls(**data)

@dataclass
class ConversationTurn:
    turn_id: str
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tool_calls: Optional[List[Dict[str, Any]]] = None
    token_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SessionState:
    session_id: str
    system_instruction: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    turns: List[ConversationTurn] = field(default_factory=list)
    compacted_summary: Optional[str] = None
    total_token_count: int = 0

    def model_dump_json(self, indent: Optional[int] = None) -> str:
        data = {
            "session_id": self.session_id,
            "system_instruction": self.system_instruction,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "turns": [t.to_dict() for t in self.turns],
            "compacted_summary": self.compacted_summary,
            "total_token_count": self.total_token_count
        }
        return json.dumps(data, indent=indent)

    @classmethod
    def model_validate_json(cls, json_str: str) -> "SessionState":
        data = json.loads(json_str)
        turns = [ConversationTurn(**t) for t in data.get("turns", [])]
        return cls(
            session_id=data["session_id"],
            system_instruction=data["system_instruction"],
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
            turns=turns,
            compacted_summary=data.get("compacted_summary"),
            total_token_count=data.get("total_token_count", 0)
        )

@dataclass
class WeeklyStateSnapshot:
    week_identifier: str
    generated_at: str
    top_topics: List[HotTopic] = field(default_factory=list)
    active_risks: List[LeadershipRisk] = field(default_factory=list)
    wins_count: int = 0
    total_message_volume: int = 0

    def model_dump_json(self, indent: Optional[int] = None) -> str:
        data = {
            "week_identifier": self.week_identifier,
            "generated_at": self.generated_at,
            "top_topics": [t.to_dict() for t in self.top_topics],
            "active_risks": [r.to_dict() for r in self.active_risks],
            "wins_count": self.wins_count,
            "total_message_volume": self.total_message_volume
        }
        return json.dumps(data, indent=indent)

    @classmethod
    def model_validate_json(cls, json_str: str) -> "WeeklyStateSnapshot":
        data = json.loads(json_str)
        topics = [HotTopic(**t) for t in data.get("top_topics", [])]
        risks = [LeadershipRisk(**r) for r in data.get("active_risks", [])]
        return cls(
            week_identifier=data["week_identifier"],
            generated_at=data["generated_at"],
            top_topics=topics,
            active_risks=risks,
            wins_count=data.get("wins_count", 0),
            total_message_volume=data.get("total_message_volume", 0)
        )

@dataclass
class ExecutiveReport:
    week_identifier: str
    executive_summary: str
    chat_group: str = "AI GTM Tech - All Team"
    report_title: str = "FDE Org Weekly Pulse & Executive Intelligence Report"
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    hot_topics: List[HotTopic] = field(default_factory=list)
    positive_wins: List[PositiveWin] = field(default_factory=list)
    areas_to_watch_risks: List[LeadershipRisk] = field(default_factory=list)
    leadership_recommendations: List[str] = field(default_factory=list)
    week_over_week_trends: Optional[Dict[str, Any]] = None
    human_approved: bool = False

    def model_dump_json(self, indent: Optional[int] = 2) -> str:
        data = {
            "week_identifier": self.week_identifier,
            "report_title": self.report_title,
            "chat_group": self.chat_group,
            "generated_at": self.generated_at,
            "executive_summary": self.executive_summary,
            "hot_topics": [t.to_dict() for t in self.hot_topics],
            "positive_wins": [w.to_dict() for w in self.positive_wins],
            "areas_to_watch_risks": [r.to_dict() for r in self.areas_to_watch_risks],
            "leadership_recommendations": self.leadership_recommendations,
            "week_over_week_trends": self.week_over_week_trends,
            "human_approved": self.human_approved
        }
        return json.dumps(data, indent=indent)
