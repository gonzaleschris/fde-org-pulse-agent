import unittest
import asyncio
from fde_pulse.memory.session_memory import AsyncSessionMemory, SYSTEM_INSTRUCTION

class TestAsyncMemory(unittest.TestCase):
    def setUp(self):
        self.memory = AsyncSessionMemory(db_path=":memory:")

    def test_session_creation_and_turns(self):
        async def run_test():
            session = await self.memory.get_or_create_session("test_sess_01")
            self.assertEqual(session.session_id, "test_sess_01")
            self.assertEqual(session.system_instruction, SYSTEM_INSTRUCTION)
            self.assertEqual(len(session.turns), 0)

            # Append user turn
            updated = await self.memory.append_turn("test_sess_01", "user", "Ingest chat logs")
            self.assertEqual(len(updated.turns), 1)
            self.assertEqual(updated.turns[0].role, "user")

            # Append model turn
            updated2 = await self.memory.append_turn("test_sess_01", "model", "Report generated")
            self.assertEqual(len(updated2.turns), 2)

        asyncio.run(run_test())

    def test_history_compaction(self):
        async def run_compaction():
            session_id = "test_sess_compaction"
            await self.memory.get_or_create_session(session_id)
            
            # Generate multiple turns with long content to exceed threshold
            for i in range(10):
                await self.memory.append_turn(
                    session_id,
                    "user" if i % 2 == 0 else "model",
                    f"Turn {i} with long enterprise text content " * 150
                )
            
            session = await self.memory.get_or_create_session(session_id)
            self.assertIsNotNone(session.compacted_summary)
            self.assertIn("[Compacted History Summary]", session.compacted_summary)

        asyncio.run(run_compaction())

if __name__ == "__main__":
    unittest.main()
