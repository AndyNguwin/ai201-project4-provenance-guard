import json
import os
from pathlib import Path


LOG_PATH = Path(os.getenv("AUDIT_LOG_PATH", "audit_log.jsonl"))
DEFAULT_LIMIT = int(os.getenv("AUDIT_LOG_LIMIT", "5"))


def write_log(entry):
    """Append one structured JSON audit entry."""
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry, sort_keys=True) + "\n")


def get_log(limit=DEFAULT_LIMIT):
    """Return the most recent audit log entries."""
    if not LOG_PATH.exists():
        return []

    with LOG_PATH.open("r", encoding="utf-8") as log_file:
        lines = log_file.readlines()

    entries = []
    for line in lines[-limit:]:
        line = line.strip()
        if line:
            entries.append(json.loads(line))

    return entries
