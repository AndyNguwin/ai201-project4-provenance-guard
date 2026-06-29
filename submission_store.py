import json
import os
from pathlib import Path


STORE_PATH = Path(os.getenv("SUBMISSION_STORE_PATH", "submissions.json"))
SUBMISSIONS = {}


def load_submissions():
    """Load persisted submissions into memory."""
    global SUBMISSIONS

    if not STORE_PATH.exists():
        SUBMISSIONS = {}
        return SUBMISSIONS

    with STORE_PATH.open("r", encoding="utf-8") as store_file:
        try:
            loaded = json.load(store_file)
        except json.JSONDecodeError:
            loaded = {}

    SUBMISSIONS = loaded if isinstance(loaded, dict) else {}
    return SUBMISSIONS


def save_submission(submission):
    """Save or replace a submission in memory and on disk."""
    SUBMISSIONS[submission["content_id"]] = submission
    _persist()
    return submission


def get_submission(content_id):
    return SUBMISSIONS.get(content_id)


def update_submission_status(content_id, status):
    submission = get_submission(content_id)
    if submission is None:
        return None

    submission["status"] = status
    _persist()
    return submission


def _persist():
    with STORE_PATH.open("w", encoding="utf-8") as store_file:
        json.dump(SUBMISSIONS, store_file, indent=2, sort_keys=True)
        store_file.write("\n")


load_submissions()
