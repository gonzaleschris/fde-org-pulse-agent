import unittest
from pathlib import Path
from fde_pulse.agent import FDEOrgPulseAgent

class TestAgentE2E(unittest.TestCase):
    def setUp(self):
        self.agent = FDEOrgPulseAgent(db_path=":memory:")
        self.sample_data = Path(__file__).resolve().parent.parent / "data" / "sample_chat_messages.json"

    def test_full_pipeline_execution(self):
        report = self.agent.run_pipeline(
            input_data_path=str(self.sample_data),
            week_identifier="2026-W36",
            previous_week_id="2026-W35"
        )
        self.assertEqual(report.week_identifier, "2026-W36")
        self.assertGreaterEqual(len(report.hot_topics), 1)
        self.assertGreaterEqual(len(report.positive_wins), 1)
        self.assertGreaterEqual(len(report.areas_to_watch_risks), 1)
        self.assertGreaterEqual(len(report.leadership_recommendations), 2)

        md = self.agent.report_tool.render_markdown(report)
        self.assertIn("Weekly Pulse & Executive Intelligence Report", md)

if __name__ == "__main__":
    unittest.main()
