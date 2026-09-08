"""Structured JSON Logging, Intent vs Outcome Tracking, and OpenTelemetry Tracing."""
import time
import logging
import json
import functools
from typing import Dict, Any, List, Optional
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """Custom structured JSON log formatter for Cloud Logging and SIEM ingestion."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if hasattr(record, "agent_intent"):
            log_entry["agent_intent"] = record.agent_intent
        if hasattr(record, "actual_outcome"):
            log_entry["actual_outcome"] = record.actual_outcome
        if hasattr(record, "telemetry"):
            log_entry["telemetry"] = record.telemetry
        return json.dumps(log_entry)

# Configure logger
logger = logging.getLogger("fde_pulse")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class Span:
    def __init__(self, name: str, parent_id: Optional[str] = None):
        self.name = name
        self.parent_id = parent_id
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.duration_ms: float = 0.0
        self.agent_intent: Optional[str] = None
        self.actual_outcome: Optional[str] = None
        self.token_usage: Dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.status = "OK"
        self.error_message: Optional[str] = None
        self.attributes: Dict[str, Any] = {}

    def set_intent_and_outcome(self, intent: str, outcome: str):
        self.agent_intent = intent
        self.actual_outcome = outcome

    def finish(self, status: str = "OK", error: Optional[str] = None):
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status = status
        self.error_message = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "agent_intent": self.agent_intent,
            "actual_outcome": self.actual_outcome,
            "token_usage": self.token_usage,
            "error": self.error_message,
            "attributes": self.attributes
        }

class TelemetryTracker:
    """Manages spans, agent intent vs outcome telemetry, and OpenTelemetry trace summaries."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelemetryTracker, cls).__new__(cls)
            cls._instance.spans: List[Span] = []
            cls._instance.metrics: Dict[str, Any] = {}
        return cls._instance

    def start_span(self, name: str) -> Span:
        span = Span(name)
        self.spans.append(span)
        return span

    def record_intent_outcome(self, step_name: str, intent: str, outcome: str, token_usage: Optional[Dict[str, int]] = None):
        """Records explicit Agent Intent vs Actual Outcome for auditability and observability scoring."""
        logger.info(
            f"Step: {step_name} | Intent: {intent} -> Outcome: {outcome}",
            extra={"agent_intent": intent, "actual_outcome": outcome, "telemetry": token_usage}
        )

    def record_metric(self, key: str, value: Any):
        self.metrics[key] = value

    def get_trace_summary(self) -> Dict[str, Any]:
        total_time_ms = sum(s.duration_ms for s in self.spans)
        return {
            "trace_id": f"trace_fde_{int(time.time())}",
            "generated_at": datetime.utcnow().isoformat(),
            "total_spans": len(self.spans),
            "total_duration_ms": round(total_time_ms, 2),
            "spans": [s.to_dict() for s in self.spans],
            "metrics": self.metrics
        }

    def export_json(self, file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.get_trace_summary(), f, indent=2)

def trace_span(span_name: str):
    """Decorator to automatically track execution latency, spans, and failures."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracker = TelemetryTracker()
            span = tracker.start_span(span_name)
            try:
                result = func(*args, **kwargs)
                span.finish(status="OK")
                return result
            except Exception as e:
                span.finish(status="ERROR", error=str(e))
                logger.error(f"Error in {span_name}: {e}")
                raise
        return wrapper
    return decorator

class StepLogger:
    @staticmethod
    def log_step(step_number: int, total_steps: int, intent: str, outcome: Optional[str] = None):
        tracker = TelemetryTracker()
        tracker.record_intent_outcome(
            step_name=f"Step {step_number}/{total_steps}",
            intent=intent,
            outcome=outcome or "In progress..."
        )
