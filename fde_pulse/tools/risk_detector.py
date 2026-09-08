"""Leadership Risk and Blocker Detector Tool with Schema Constraints."""
from typing import List, Optional
from ..models.schemas import ChatMessage, LeadershipRisk
from ..services.llm_client import GeminiLLMClient

class LeadershipRiskDetectorTool:
    """Tool to detect operational bottlenecks, 429 quota ceilings, and VPC-SC perimeter blockers."""

    def __init__(self, llm_client: Optional[GeminiLLMClient] = None):
        self.llm_client = llm_client or GeminiLLMClient()

    def detect_risks(self, messages: List[ChatMessage]) -> List[LeadershipRisk]:
        """Classifies operational friction and assigns severity (P0, P1, P2) with actionable mitigation.
        
        Args:
            messages: List of sanitized ChatMessage objects.

        Returns:
            List of validated LeadershipRisk instances.
        """
        combined_text = "\n".join([f"[{m.sender} ({m.role})]: {m.content}" for m in messages])
        prompt = (
            f"Review the following internal FDE chat messages for risks, customer blockers, 429 rate limits, "
            f"quota ceilings, or security perimeter issues:\n\n"
            f"{combined_text}\n\n"
            f"Identify the highest priority risk. Provide risk_id, severity ('P0', 'P1', or 'P2'), headline, "
            f"friction_area, affected_teams_or_customers, symptoms/evidence, and suggested_mitigation for leadership."
        )
        system_inst = "You are an FDE Operations Director identifying and mitigating operational risks."
        
        risk = self.llm_client.generate_structured(
            prompt=prompt,
            system_instruction=system_inst,
            response_schema=LeadershipRisk,
            task_type="classification"
        )
        return [risk]
