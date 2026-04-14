import numpy as np
import pandas as pd
import os

# Make sure folder exists
os.makedirs("data/simulated", exist_ok=True)
np.random.seed(42)

rows = 5000

data = pd.DataFrame({
    "battery_voltage": np.random.normal(12.6, 0.4, rows),
    "engine_temp": np.random.normal(90, 10, rows),
    "vibration": np.random.normal(0.3, 0.1, rows),
    "vehicle_age_days": np.random.randint(30, 3000, rows),
})

# Failure logic (hidden pattern)
data["failure"] = (
    (data["battery_voltage"] < 11.8) |
    (data["engine_temp"] > 110) |
    (data["vibration"] > 0.6)
).astype(int)

data.to_csv("data/simulated/vehicle_telemetry.csv", index=False)
