"""Automation rules engine.

Rules live in rules.json. Each rule has a condition and an action:

  {"name": "...", "when": {"metric": "anomaly_count", "op": ">", "value": 5},
   "category": "sensor" (optional), "action": "alert" | "log" | "quarantine"}

Metrics: anomaly_count, rows, cleaning_steps, <column>_mean, <column>_max, <column>_min
"""
import json
import operator

from . import config

OPS = {">": operator.gt, "<": operator.lt, ">=": operator.ge,
       "<=": operator.le, "==": operator.eq}

DEFAULT_RULES = [
    {"name": "Many anomalies", "when": {"metric": "anomaly_count", "op": ">", "value": 3},
     "action": "alert"},
    {"name": "Overheating sensor", "category": "sensor",
     "when": {"metric": "temperature_max", "op": ">", "value": 80}, "action": "alert"},
    {"name": "Large file", "when": {"metric": "rows", "op": ">", "value": 100000},
     "action": "log"},
]


def load_rules() -> list[dict]:
    if not config.RULES_FILE.exists():
        config.RULES_FILE.write_text(json.dumps(DEFAULT_RULES, indent=2))
    return json.loads(config.RULES_FILE.read_text())


def build_metrics(summary: dict, anomalies: dict, cleaning_log: list[str]) -> dict:
    metrics = {
        "rows": summary["rows"],
        "anomaly_count": sum(a["count"] for a in anomalies.values()),
        "cleaning_steps": len(cleaning_log),
    }
    for col, st in summary["numeric_stats"].items():
        metrics[f"{col}_mean"] = st["mean"]
        metrics[f"{col}_max"] = st["max"]
        metrics[f"{col}_min"] = st["min"]
    return metrics


def evaluate(rules: list[dict], metrics: dict, category: str) -> list[dict]:
    triggered = []
    for rule in rules:
        if rule.get("category") not in (None, category):
            continue
        cond = rule["when"]
        value = metrics.get(cond["metric"])
        if value is not None and OPS[cond["op"]](value, cond["value"]):
            triggered.append({"rule": rule["name"], "action": rule["action"],
                              "metric": cond["metric"], "actual": value})
    return triggered
