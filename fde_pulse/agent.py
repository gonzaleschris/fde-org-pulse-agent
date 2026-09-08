"""Main Entry Point and CLI Orchestrator for FDE Org Pulse Agent."""
import argparse
import asyncio
import sys
import json
from pathlib import Path

from .config import TARGET_CHAT_GROUP, ORG_NAME
from .tools.chat_ingestion import ChatIngestionTool
from .tools.topic_analyzer import TopicAndWinsAnalyzerTool
from .tools.risk_detector import LeadershipRiskDetectorTool
from .tools.report_builder import ExecutiveReportBuilderTool
from .agents.topic_hunter import TopicHunterAgent
from .agents.risk_detector_agent import RiskDetectorAgent
from .agents.coordinator import CoordinatorAgent
from .memory.state_store import StateStore
from .memory.session_memory import AsyncSessionMemory
from .services.llm_client import GeminiLLMClient
from .services.secret_manager import SecretManagerService
from .observability.telemetry import TelemetryTracker, logger

class FDEOrgPulseAgent:
    """Production Multi-Agent Coordinator for Google Cloud FDE Org Pulse."""

    def __init__(self, db_path: str = ":memory:"):
        self.secret_service = SecretManagerService()
        self.llm_client = GeminiLLMClient(secret_service=self.secret_service)
        
        # Tools
        self.ingestion_tool = ChatIngestionTool(target_channel=TARGET_CHAT_GROUP)
        self.topic_tool = TopicAndWinsAnalyzerTool(llm_client=self.llm_client)
        self.risk_tool = LeadershipRiskDetectorTool(llm_client=self.llm_client)
        self.report_tool = ExecutiveReportBuilderTool()
        
        # Sub-Agents
        self.topic_hunter = TopicHunterAgent(self.topic_tool)
        self.risk_detector = RiskDetectorAgent(self.risk_tool)
        
        # Memory
        self.state_store = StateStore(db_path=db_path)
        self.session_memory = AsyncSessionMemory(db_path=db_path)
        
        # Master Coordinator
        self.coordinator = CoordinatorAgent(
            ingestion_tool=self.ingestion_tool,
            topic_hunter=self.topic_hunter,
            risk_detector=self.risk_detector,
            report_builder=self.report_tool,
            state_store=self.state_store,
            session_memory=self.session_memory
        )
        self.telemetry = TelemetryTracker()

    def run_pipeline(
        self,
        input_data_path: str,
        week_identifier: str = "2026-W36",
        previous_week_id: str = "2026-W35",
        require_human_approval: bool = True
    ):
        """Synchronous wrapper around async multi-agent coordinator orchestration."""
        return asyncio.run(
            self.coordinator.orchestrate_pulse(
                input_data_path=input_data_path,
                week_identifier=week_identifier,
                previous_week_id=previous_week_id,
                require_human_approval=require_human_approval
            )
        )

def main():
    parser = argparse.ArgumentParser(description="FDE Org Pulse & Weekly Intelligence Agent CLI")
    parser.add_argument("--input", "-i", default="data/sample_chat_messages.json", help="Path to input chat JSON file")
    parser.add_argument("--week", "-w", default="2026-W36", help="Week identifier (e.g. 2026-W36)")
    parser.add_argument("--prev-week", "-p", default="2026-W35", help="Previous week identifier for delta comparison")
    parser.add_argument("--output-dir", "-o", default="outputs", help="Directory to save generated reports")
    parser.add_argument("--format", "-f", choices=["markdown", "json", "all"], default="all", help="Output format")
    parser.add_argument("--export-telemetry", action="store_true", help="Export OpenTelemetry trace json")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    agent = FDEOrgPulseAgent()
    logger.info(f"Starting FDE Org Pulse Agent for week {args.week}...")
    
    report = agent.run_pipeline(
        input_data_path=args.input,
        week_identifier=args.week,
        previous_week_id=args.prev_week
    )

    md_output = agent.report_tool.render_markdown(report)

    if args.format in ["markdown", "all"]:
        md_file = out_dir / f"fde_pulse_report_{args.week}.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_output)
        logger.info(f"Saved Markdown report to: {md_file}")

    if args.format in ["json", "all"]:
        json_file = out_dir / f"fde_pulse_report_{args.week}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))
        logger.info(f"Saved JSON report to: {json_file}")

    if args.export_telemetry:
        telemetry_file = out_dir / f"trace_{args.week}.json"
        agent.telemetry.export_json(str(telemetry_file))
        logger.info(f"Exported trace telemetry to: {telemetry_file}")

    print("\n" + "="*80)
    print(md_output)
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
