import json
import os
from pathlib import Path


LOG_PATH = Path(os.getenv("AUDIT_LOG_PATH", "audit_log.jsonl"))
DEFAULT_LIMIT = int(os.getenv("AUDIT_LOG_LIMIT", "50"))


def write_log(entry):
    """Append one structured JSON audit entry."""
    if LOG_PATH.exists() and LOG_PATH.stat().st_size > 0:
        with LOG_PATH.open("rb") as log_file:
            log_file.seek(-1, os.SEEK_END)
            if log_file.read(1) != b"\n":
                with LOG_PATH.open("a", encoding="utf-8") as append_file:
                    append_file.write("\n")

    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry, sort_keys=True) + "\n")


def get_log(limit=DEFAULT_LIMIT):
    """Return the most recent audit log entries."""
    entries = get_all_log_entries()
    return entries[-limit:]


def get_all_log_entries():
    """Return all parseable audit log entries."""
    if not LOG_PATH.exists():
        return []

    with LOG_PATH.open("r", encoding="utf-8") as log_file:
        lines = log_file.readlines()

    entries = []
    for line in lines:
        line = line.strip().lstrip("\ufeff")
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return entries


def find_submission(content_id):
    """Find the original submission audit entry for a content ID."""
    for entry in reversed(get_all_log_entries()):
        if (
            entry.get("event_type") == "submission"
            and entry.get("content_id") == content_id
        ):
            return entry

    return None
