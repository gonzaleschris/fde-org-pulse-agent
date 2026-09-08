"""Specialist Sub-Agent for Operational Friction and Leadership Risk Triage."""
from typing import List
from ..models.schemas import ChatMessage, LeadershipRisk
from ..tools.risk_detector import LeadershipRiskDetectorTool
from ..observability.telemetry import trace_span

class RiskDetectorAgent:
    """Specialist worker agent responsible for categorizing risks, 429 quota ceilings, and VPC-SC blockers."""

    def __init__(self, risk_tool: LeadershipRiskDetectorTool):
        self.tool = risk_tool

    @trace_span("RiskDetectorAgent.execute")
    def execute(self, messages: List[ChatMessage]) -> List[LeadershipRisk]:
        """Executes risk triage and priority severity assignment."""
        return self.tool.detect_risks(messages)
