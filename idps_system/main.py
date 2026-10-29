"""CLI for the Intelligent Data Processing and Automation System.

  python main.py once            process everything currently in inbox/
  python main.py watch           keep watching inbox/ and process new files
  python main.py process FILE    process one specific file (copied into inbox first)
"""
import argparse
import shutil
from pathlib import Path

from idps import config
from idps.watcher import scan_once, watch


def main() -> None:
    parser = argparse.ArgumentParser(description="Intelligent Data Processing and Automation System")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("once", help="process all files in inbox/ once")
    w = sub.add_parser("watch", help="watch inbox/ continuously")
    w.add_argument("--interval", type=int, default=config.POLL_SECONDS)
    p = sub.add_parser("process", help="process a single file")
    p.add_argument("file")

    args = parser.parse_args()
    if args.cmd == "once":
        print(f"Processed {scan_once()} file(s).")
    elif args.cmd == "watch":
        watch(args.interval)
    elif args.cmd == "process":
        src = Path(args.file)
        shutil.copy(src, config.INBOX / src.name)
        print(f"Processed {scan_once()} file(s).")


if __name__ == "__main__":
    main()
