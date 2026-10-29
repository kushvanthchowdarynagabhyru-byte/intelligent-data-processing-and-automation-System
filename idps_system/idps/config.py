"""Paths and settings."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INBOX = BASE_DIR / "inbox"          # drop new files here
PROCESSED = BASE_DIR / "processed"  # successfully handled files
FAILED = BASE_DIR / "failed"        # files that raised errors
OUTPUT = BASE_DIR / "output"        # cleaned data + reports
LOGS = BASE_DIR / "logs"
RULES_FILE = BASE_DIR / "rules.json"

SUPPORTED = {".csv", ".json", ".xlsx", ".xls"}
POLL_SECONDS = 5

for d in (INBOX, PROCESSED, FAILED, OUTPUT, LOGS):
    d.mkdir(exist_ok=True)
