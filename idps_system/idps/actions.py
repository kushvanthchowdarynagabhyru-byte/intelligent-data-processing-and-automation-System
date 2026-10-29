"""Actions: logging, alerts, reports, file movement."""
import json
import shutil
from datetime import datetime
from pathlib import Path

from . import config


def log(message: str) -> None:
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {message}"
    print(line)
    with open(config.LOGS / "automation.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def send_alert(file_name: str, trigger: dict) -> None:
    """Base version writes alerts to a log file. Swap in email/Slack/webhook here."""
    msg = (f"ALERT [{file_name}] rule '{trigger['rule']}' "
           f"({trigger['metric']} = {trigger['actual']})")
    log(msg)
    with open(config.LOGS / "alerts.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')}  {msg}\n")


def write_report(stem: str, report: dict) -> Path:
    path = config.OUTPUT / f"{stem}_report.json"
    path.write_text(json.dumps(report, indent=2, default=str))

    md = [f"# Report: {report['file']}", "",
          f"- Category: **{report['category']}**",
          f"- Rows: {report['summary']['rows']}",
          f"- Processed at: {report['processed_at']}", "",
          "## Cleaning steps"]
    md += [f"- {s}" for s in report["cleaning"]] or ["- none needed"]
    md += ["", "## Anomalies"]
    md += [f"- `{c}`: {a['count']} outliers (e.g. {a['values'][:3]})"
           for c, a in report["anomalies"].items()] or ["- none found"]
    md += ["", "## Triggered rules"]
    md += [f"- **{t['rule']}** → {t['action']} ({t['metric']} = {t['actual']})"
           for t in report["triggered_rules"]] or ["- none"]
    (config.OUTPUT / f"{stem}_report.md").write_text("\n".join(md))
    return path


def move_file(src: Path, dest_dir: Path) -> Path:
    dest = dest_dir / f"{datetime.now():%Y%m%d_%H%M%S}_{src.name}"
    shutil.move(str(src), dest)
    return dest
