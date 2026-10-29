"""Processes a single file end to end."""
from datetime import datetime
from pathlib import Path

from . import actions, analyzer, cleaner, config, detector, rules


def process_file(path: Path) -> dict:
    actions.log(f"Processing {path.name}")
    try:
        raw = detector.load_file(path)
        category = detector.detect_category(raw)
        df, cleaning_log = cleaner.clean(raw)
        summary = analyzer.summarize(df)
        anomalies = analyzer.find_anomalies(df)

        metrics = rules.build_metrics(summary, anomalies, cleaning_log)
        triggered = rules.evaluate(rules.load_rules(), metrics, category)

        quarantine = False
        for t in triggered:
            if t["action"] == "alert":
                actions.send_alert(path.name, t)
            elif t["action"] == "quarantine":
                quarantine = True
                actions.send_alert(path.name, t)
            else:
                actions.log(f"Rule '{t['rule']}' triggered ({t['metric']}={t['actual']})")

        stem = path.stem
        df.to_csv(config.OUTPUT / f"{stem}_clean.csv", index=False)
        report = {
            "file": path.name, "category": category,
            "processed_at": datetime.now().isoformat(timespec="seconds"),
            "cleaning": cleaning_log, "summary": summary,
            "anomalies": anomalies, "triggered_rules": triggered,
        }
        actions.write_report(stem, report)

        actions.move_file(path, config.FAILED if quarantine else config.PROCESSED)
        actions.log(f"Finished {path.name}: category={category}, "
                    f"anomalies={metrics['anomaly_count']}, rules_triggered={len(triggered)}")
        return report
    except Exception as exc:
        actions.log(f"ERROR processing {path.name}: {exc}")
        actions.move_file(path, config.FAILED)
        return {"file": path.name, "error": str(exc)}
