"""
Structured logging for the MoodArc agent pipeline.
Logs each agent step with timing, inputs, and outputs.
"""

import logging
import json
import time
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_log_file = LOG_DIR / f"moodarc_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(_log_file),
        logging.StreamHandler(),
    ],
)

_logger = logging.getLogger("moodarc")


class AgentStepLogger:
    """Context manager that logs an agent step with timing."""

    def __init__(self, step_name: str, input_summary: str = ""):
        self.step_name = step_name
        self.input_summary = input_summary
        self.start_time = 0.0

    def __enter__(self):
        self.start_time = time.time()
        _logger.info(f"[START] {self.step_name} | input={self.input_summary!r}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = round(time.time() - self.start_time, 3)
        if exc_type:
            _logger.error(
                f"[FAIL]  {self.step_name} | elapsed={elapsed}s | error={exc_val}"
            )
        else:
            _logger.info(f"[DONE]  {self.step_name} | elapsed={elapsed}s")
        return False


def log_journey(user_input: str, result: dict) -> None:
    """Append a complete journey record to the daily log as JSON."""
    record = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "arc": result.get("arc", []),
        "confidence": result.get("confidence", None),
        "song_count": len(result.get("playlist", [])),
    }
    _logger.info(f"[JOURNEY] {json.dumps(record)}")


def log_guardrail_trigger(keyword: str, user_input: str) -> None:
    _logger.warning(f"[GUARDRAIL] keyword={keyword!r} | input={user_input[:80]!r}")


def get_logger(name: str = "moodarc") -> logging.Logger:
    return logging.getLogger(name)
