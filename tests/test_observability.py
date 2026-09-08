import unittest
from pathlib import Path
from fde_pulse.observability.telemetry import TelemetryTracker, trace_span

class TestObservability(unittest.TestCase):
    def setUp(self):
        self.telemetry = TelemetryTracker()

    def test_start_and_finish_span(self):
        span = self.telemetry.start_span("test_span")
        span.finish(status="OK")
        self.assertEqual(span.status, "OK")
        self.assertGreaterEqual(span.duration_ms, 0)

    def test_trace_span_decorator(self):
        @trace_span("decorated_action")
        def sample_action(x: int) -> int:
            return x * 2

        result = sample_action(5)
        self.assertEqual(result, 10)
        summary = self.telemetry.get_trace_summary()
        self.assertGreaterEqual(summary["total_spans"], 1)

    def test_export_json(self):
        out_file = Path(__file__).resolve().parent.parent / "outputs" / "test_trace.json"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        self.telemetry.export_json(str(out_file))
        self.assertTrue(out_file.exists())
        self.assertGreater(out_file.stat().st_size, 10)

if __name__ == "__main__":
    unittest.main()
