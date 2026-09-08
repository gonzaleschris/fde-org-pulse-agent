import unittest
from datetime import datetime
from fde_pulse.memory.state_store import StateStore
from fde_pulse.models.schemas import WeeklyStateSnapshot, HotTopic, LeadershipRisk

class TestMemory(unittest.TestCase):
    def setUp(self):
        self.store = StateStore(db_path=":memory:")

    def test_save_and_get_snapshot(self):
        topic = HotTopic(
            title="ADK Scaling",
            category="ADK",
            mentions_count=5,
            summary="Rapid testing",
            impact_level="High",
            key_contributors=["Alice"]
        )
        snapshot = WeeklyStateSnapshot(
            week_identifier="2026-W36",
            generated_at=datetime.utcnow().isoformat(),
            top_topics=[topic],
            active_risks=[],
            wins_count=2,
            total_message_volume=10
        )
        self.store.save_weekly_snapshot(snapshot)
        retrieved = self.store.get_weekly_snapshot("2026-W36")

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.week_identifier, "2026-W36")
        self.assertEqual(retrieved.wins_count, 2)
        self.assertEqual(len(retrieved.top_topics), 1)

    def test_week_over_week_delta(self):
        snap1 = WeeklyStateSnapshot(
            week_identifier="2026-W35",
            generated_at=datetime.utcnow().isoformat(),
            top_topics=[],
            active_risks=[],
            wins_count=1,
            total_message_volume=5
        )
        self.store.save_weekly_snapshot(snap1)

        snap2 = WeeklyStateSnapshot(
            week_identifier="2026-W36",
            generated_at=datetime.utcnow().isoformat(),
            top_topics=[],
            active_risks=[],
            wins_count=3,
            total_message_volume=15
        )
        delta = self.store.compute_week_over_week_delta(snap2, "2026-W35")
        self.assertIn("Message Activity Delta", delta)
        self.assertIn("+10 messages", delta["Message Activity Delta"])

if __name__ == "__main__":
    unittest.main()
