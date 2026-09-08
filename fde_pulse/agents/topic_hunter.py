"""Specialist Sub-Agent for Topic Hunting and Milestone Extraction."""
from typing import List, Tuple
from ..models.schemas import ChatMessage, HotTopic, PositiveWin
from ..tools.topic_analyzer import TopicAndWinsAnalyzerTool
from ..observability.telemetry import trace_span

class TopicHunterAgent:
    """Specialist worker agent responsible for extracting technical trends and customer milestones."""

    def __init__(self, analyzer_tool: TopicAndWinsAnalyzerTool):
        self.tool = analyzer_tool

    @trace_span("TopicHunterAgent.execute")
    def execute(self, messages: List[ChatMessage]) -> Tuple[List[HotTopic], List[PositiveWin]]:
        """Executes topic extraction and customer win detection."""
        topics = self.tool.analyze_topics(messages)
        wins = self.tool.analyze_wins(messages)
        return topics, wins
