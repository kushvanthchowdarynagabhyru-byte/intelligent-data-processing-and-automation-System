"""Creates sample files in inbox/ (a sensor file with spikes, a messy sales file)."""
import numpy as np
import pandas as pd

from idps import config

rng = np.random.default_rng(7)

# 1) sensor readings with a few injected spikes
n = 150
sensor = pd.DataFrame({
    "Device ID": rng.choice(["S-01", "S-02", "S-03"], n),
    "Timestamp": pd.date_range("2026-10-01", periods=n, freq="h").strftime("%Y-%m-%d %H:%M"),
    "Temperature": rng.normal(45, 4, n).round(1),
    "Humidity": rng.normal(55, 6, n).round(1),
})
sensor.loc[[20, 60, 100, 130], "Temperature"] = [95.0, 102.5, 98.1, 110.0]
sensor.loc[rng.choice(n, 6, replace=False), "Humidity"] = None
sensor.to_csv(config.INBOX / "sensor_readings.csv", index=False)

# 2) messy sales data
m = 80
sales = pd.DataFrame({
    "Order ID": np.arange(5000, 5000 + m),
    "Customer": rng.choice(["  Asha", "Ravi ", "Meena", "Kiran"], m),
    "Product": rng.choice(["Laptop", "Phone", "Tablet"], m),
    "Quantity": rng.integers(1, 6, m),
    "Total": [f"${v:,.0f}" for v in rng.integers(300, 3000, m)],
})
sales = pd.concat([sales, sales.sample(5, random_state=2)], ignore_index=True)
sales.to_csv(config.INBOX / "sales_orders.csv", index=False)

print("Sample files written to", config.INBOX)
