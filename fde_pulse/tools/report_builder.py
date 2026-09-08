"""Executive Report Builder Tool with Multi-Format Rendering."""
from typing import List, Dict, Any, Optional
from ..models.schemas import (
    ExecutiveReport, HotTopic, PositiveWin, LeadershipRisk, ChatIngestionBatch
)
from ..config import TARGET_CHAT_GROUP, ORG_NAME

class ExecutiveReportBuilderTool:
    """Formats findings into polished Markdown, JSON, and leadership briefs."""

    def build_report(
        self,
        batch: ChatIngestionBatch,
        topics: List[HotTopic],
        wins: List[PositiveWin],
        risks: List[LeadershipRisk],
        week_over_week_trends: Optional[Dict[str, Any]] = None,
        human_approved: bool = False
    ) -> ExecutiveReport:
        """Synthesizes structured items into a cohesive ExecutiveReport.
        
        Args:
            batch: ChatIngestionBatch container.
            topics: Extracted HotTopic items.
            wins: PositiveWin customer milestones.
            risks: Detected LeadershipRisk items.
            week_over_week_trends: Historical trend delta dictionary.
            human_approved: Boolean indicating human-in-the-loop review.

        Returns:
            Fully populated ExecutiveReport.
        """
        summary = (
            f"During {batch.week_identifier}, the '{TARGET_CHAT_GROUP}' group recorded {batch.total_messages} messages "
            f"across {batch.active_contributors} active contributors. Core momentum centered on {len(topics)} primary technical tracks "
            f"and {len(wins)} customer/project milestones. {len(risks)} operational areas require leadership attention, "
            f"specifically around quota management and VPC-SC configuration."
        )

        recommendations = [
            "⚡ Expand Gemini 2.0 Flash Quotas: Pre-provision TPM/RPM for high-velocity customer agent deployments to prevent 429 throttling.",
            "🛡️ Standardize VPC-SC & Security Bridges: Publish repeatable Terraform modules for cross-perimeter enterprise agent deployments.",
            "🚀 Codify Winning Agent Patterns: Democratize top field architectures (ADK coordinator-worker pattern) into the FDE knowledge repository.",
            "⏱️ Guard 8-12 Week Delivery Boundaries: Re-align customer steering committees early if scope expands beyond initial agent MVP agreements."
        ]

        return ExecutiveReport(
            week_identifier=batch.week_identifier,
            chat_group=TARGET_CHAT_GROUP,
            report_title=f"{ORG_NAME} Weekly Pulse & Executive Intelligence Report",
            executive_summary=summary,
            hot_topics=topics,
            positive_wins=wins,
            areas_to_watch_risks=risks,
            leadership_recommendations=recommendations,
            week_over_week_trends=week_over_week_trends,
            human_approved=human_approved
        )

    def render_markdown(self, report: ExecutiveReport) -> str:
        """Generates clean GitHub-flavored Markdown for executive dissemination."""
        md = []
        approval_badge = "✅ **[Human-in-the-Loop Approved]**" if report.human_approved else "⚠️ **[Pending Leadership Review]**"
        
        md.append(f"# 📡 {report.report_title}")
        md.append(f"**Week:** `{report.week_identifier}` | **Source Chat:** `{report.chat_group}` | **Status:** {approval_badge}\n")
        md.append("---")
        
        md.append("## 📌 Executive Summary")
        md.append(report.executive_summary + "\n")

        md.append("## 🔥 Hot Topics & Emerging Technical Patterns")
        if report.hot_topics:
            for t in report.hot_topics:
                contribs = ", ".join(t.key_contributors) if t.key_contributors else "Team"
                md.append(f"### 🔹 {t.title} `[{t.impact_level} Impact | {t.mentions_count} Mentions]`")
                md.append(f"{t.summary}")
                md.append(f"*Key Contributors:* {contribs}\n")
        else:
            md.append("No dominant technical spikes observed this period.\n")

        md.append("## 🏆 Positive Wins & Customer Milestones")
        if report.positive_wins:
            for w in report.positive_wins:
                leads = ", ".join(w.lead_engineers) if w.lead_engineers else "FDE Team"
                metrics = f" — *Metric:* **{w.impact_metrics}**" if w.impact_metrics else ""
                md.append(f"- **{w.headline}** ({w.customer_or_project}){metrics}")
                md.append(f"  > *Details:* {w.description}")
                md.append(f"  > *Lead:* {leads}\n")
        else:
            md.append("Standard ongoing delivery engagements.\n")

        md.append("## ⚠️ Areas to Watch (Leadership Risks & Friction Points)")
        if report.areas_to_watch_risks:
            for r in report.areas_to_watch_risks:
                md.append(f"### 🚨 [{r.severity}] {r.headline}")
                md.append(f"- **Friction Area:** {r.friction_area}")
                md.append(f"- **Symptoms / Evidence:** {r.symptoms}")
                md.append(f"- **Suggested Mitigation:** 💡 *{r.suggested_mitigation}*\n")
        else:
            md.append("No critical P0/P1 blockers identified.\n")

        md.append("## 🎯 Actionable Leadership Recommendations")
        for rec in report.leadership_recommendations:
            md.append(f"- {rec}")
        md.append("")

        if report.week_over_week_trends:
            md.append("## 📈 Week-over-Week Trend Analysis")
            for k, v in report.week_over_week_trends.items():
                md.append(f"- **{k}:** {v}")
            md.append("")

        return "\n".join(md)
