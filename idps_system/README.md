# Intelligent Data Processing and Automation System (base project)

Drop a data file into `inbox/` and the system handles the rest, automatically:

```
inbox/ -> detect type & category -> auto-clean -> summarize + find anomalies
       -> evaluate automation rules (alerts / quarantine) -> report + clean CSV -> processed/ or failed/
```

## Structure
```
main.py                  CLI (once / watch / process)
generate_sample_data.py  puts demo files in inbox/
rules.json               automation rules (auto-created on first run, edit freely)
idps/
  config.py              folders and settings
  detector.py            loads csv/json/xlsx, guesses category (sales, sensor, finance, hr)
  cleaner.py             dedupe, type conversion, trimming, missing-value fill
  analyzer.py            summary stats + IQR outlier detection
  rules.py               rule engine (JSON conditions -> actions)
  actions.py             logging, alerts, reports, file moves
  processor.py           processes one file end to end
  watcher.py             polling loop that watches inbox/
```

## Run
```bash
pip install -r requirements.txt
python generate_sample_data.py
python main.py once          # or: python main.py watch
```
Results: `output/` (clean CSV, JSON + Markdown report), `logs/automation.log`, `logs/alerts.log`.

## Rules (rules.json)
```json
{"name": "Overheating sensor", "category": "sensor",
 "when": {"metric": "temperature_max", "op": ">", "value": 80}, "action": "alert"}
```
Metrics: `rows`, `anomaly_count`, `cleaning_steps`, and `<column>_mean/_min/_max`.
Actions: `alert`, `log`, `quarantine` (moves the file to `failed/`).

## Ideas to extend
- Send alerts by email, Slack or webhook in `actions.send_alert`
- Replace IQR with Isolation Forest (scikit-learn)
- Add a cron/Airflow schedule or a Streamlit dashboard
- Use an LLM to write the plain-English report summary
