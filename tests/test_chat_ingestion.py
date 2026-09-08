import unittest
import json
from pathlib import Path
from fde_pulse.tools.chat_ingestion import ChatIngestionTool

class TestChatIngestion(unittest.TestCase):
    def setUp(self):
        self.tool = ChatIngestionTool(target_channel="AI GTM Tech - All Team")

    def test_sanitize_content(self):
        dirty_text = "Here is my secret AIzaSyD3ExampleKey1234567890abcdef and token Bearer eyJhbGciOi"
        sanitized = self.tool.sanitize_content(dirty_text)
        self.assertIn("[REDACTED_API_KEY]", sanitized)
        self.assertIn("[REDACTED_TOKEN]", sanitized)
        self.assertNotIn("AIzaSyD3ExampleKey1234567890abcdef", sanitized)

    def test_ingest_from_file(self):
        sample_path = Path(__file__).resolve().parent.parent / "data" / "sample_chat_messages.json"
        batch = self.tool.ingest_from_file(sample_path, week_identifier="2026-W36")
        self.assertGreater(batch.total_messages, 0)
        self.assertGreater(batch.active_contributors, 0)
        self.assertEqual(batch.messages[0].channel, "AI GTM Tech - All Team")

if __name__ == "__main__":
    unittest.main()
