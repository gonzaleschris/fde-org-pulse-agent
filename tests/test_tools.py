import unittest
from fde_pulse.models.schemas import ChatMessage, ChatIngestionBatch
from fde_pulse.tools.topic_analyzer import TopicAndWinsAnalyzerTool
from fde_pulse.tools.risk_detector import LeadershipRiskDetectorTool
from fde_pulse.tools.report_builder import ExecutiveReportBuilderTool

class TestTools(unittest.TestCase):
    def setUp(self):
        self.topic_tool = TopicAndWinsAnalyzerTool()
        self.risk_tool = LeadershipRiskDetectorTool()
        self.report_tool = ExecutiveReportBuilderTool()

        self.messages = [
            ChatMessage(
                id="1",
                sender="Alex",
                role="FDE",
                timestamp="2026-09-01T10:00:00Z",
                content="Shipped retail customer agent using Gemini 2.0 Flash!",
                reactions_count=10,
                thread_replies_count=2,
                channel="AI GTM Tech - All Team"
            ),
            ChatMessage(
                id="2",
                sender="Priya",
                role="FDE",
                timestamp="2026-09-01T11:00:00Z",
                content="Encountered 429 rate limit quota exceeded on Vertex AI.",
                reactions_count=5,
                thread_replies_count=4,
                channel="AI GTM Tech - All Team"
            )
        ]

    def test_topic_and_wins_extraction(self):
        topics = self.topic_tool.analyze_topics(self.messages)
        wins = self.topic_tool.analyze_wins(self.messages)
        self.assertGreaterEqual(len(topics), 1)
        self.assertGreaterEqual(len(wins), 1)
        self.assertTrue(len(wins[0].headline) > 0)
        self.assertIn("ADK", topics[0].title)

    def test_risk_detection(self):
        risks = self.risk_tool.detect_risks(self.messages)
        self.assertGreaterEqual(len(risks), 1)
        self.assertEqual(risks[0].severity, "P0")
        self.assertIn("Quota", risks[0].headline)

    def test_report_builder_and_markdown(self):
        batch = ChatIngestionBatch(
            week_identifier="2026-W36",
            total_messages=2,
            active_contributors=2,
            messages=self.messages
        )
        topics = self.topic_tool.analyze_topics(self.messages)
        wins = self.topic_tool.analyze_wins(self.messages)
        risks = self.risk_tool.detect_risks(self.messages)

        report = self.report_tool.build_report(batch, topics, wins, risks, human_approved=True)
        md = self.report_tool.render_markdown(report)

        self.assertIn("Weekly Pulse", md)
        self.assertIn("Hot Topics", md)
        self.assertIn("Positive Wins", md)
        self.assertIn("Areas to Watch", md)
        self.assertIn("Human-in-the-Loop Approved", md)

if __name__ == "__main__":
    unittest.main()
