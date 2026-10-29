"""Polling watcher: no extra dependencies, works everywhere."""
import time
from pathlib import Path

from . import actions, config
from .processor import process_file


def scan_once() -> int:
    files = [p for p in sorted(config.INBOX.iterdir())
             if p.is_file() and p.suffix.lower() in config.SUPPORTED]
    for p in files:
        process_file(Path(p))
    return len(files)


def watch(interval: int = config.POLL_SECONDS) -> None:
    actions.log(f"Watching {config.INBOX} every {interval}s (Ctrl+C to stop)")
    try:
        while True:
            scan_once()
            time.sleep(interval)
    except KeyboardInterrupt:
        actions.log("Watcher stopped")
