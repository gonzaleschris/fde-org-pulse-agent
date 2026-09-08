import unittest
from fde_pulse.tools.topic_analyzer import TopicAndWinsAnalyzerTool
from fde_pulse.tools.risk_detector import LeadershipRiskDetectorTool
from fde_pulse.agents.topic_hunter import TopicHunterAgent
from fde_pulse.agents.risk_detector_agent import RiskDetectorAgent
from fde_pulse.models.schemas import ChatMessage

class TestMultiAgent(unittest.TestCase):
    def setUp(self):
        self.topic_tool = TopicAndWinsAnalyzerTool()
        self.risk_tool = LeadershipRiskDetectorTool()
        self.topic_hunter = TopicHunterAgent(self.topic_tool)
        self.risk_detector = RiskDetectorAgent(self.risk_tool)

        self.messages = [
            ChatMessage(
                id="msg_01",
                sender="Alex",
                role="FDE",
                timestamp="2026-09-01T10:00:00Z",
                content="Shipped retail agent pilot with Gemini 2.0 Flash in 4 days!",
                channel="AI GTM Tech - All Team"
            ),
            ChatMessage(
                id="msg_02",
                sender="Priya",
                role="FDE",
                timestamp="2026-09-01T11:00:00Z",
                content="Encountered 429 quota rate limit ceiling during load test.",
                channel="AI GTM Tech - All Team"
            )
        ]

    def test_topic_hunter_sub_agent(self):
        topics, wins = self.topic_hunter.execute(self.messages)
        self.assertGreaterEqual(len(topics), 1)
        self.assertGreaterEqual(len(wins), 1)
        self.assertIn("ADK", topics[0].title)

    def test_risk_detector_sub_agent(self):
        risks = self.risk_detector.execute(self.messages)
        self.assertGreaterEqual(len(risks), 1)
        self.assertEqual(risks[0].severity, "P0")

if __name__ == "__main__":
    unittest.main()
