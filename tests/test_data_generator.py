"""
tests/test_data_generator.py
Generate test data for the system
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import random

def generate_engine_data(num_samples=1000):
    """Generate synthetic engine data"""
    print(f"Generating {num_samples} engine data samples...")
    
    np.random.seed(42)
    
    # Generate normal operating data
    normal_data = {
        'engine_rpm': np.random.uniform(1000, 3500, int(num_samples * 0.8)),
        'lub_oil_pressure': np.random.uniform(1.8, 2.8, int(num_samples * 0.8)),
        'fuel_pressure': np.random.uniform(2.0, 2.8, int(num_samples * 0.8)),
        'coolant_pressure': np.random.uniform(1.0, 1.6, int(num_samples * 0.8)),
        'lub_oil_temp': np.random.uniform(80, 105, int(num_samples * 0.8)),
        'coolant_temp': np.random.uniform(75, 95, int(num_samples * 0.8)),
    }
    
    # Generate failure data
    failure_data = {
        'engine_rpm': np.random.uniform(3500, 7000, int(num_samples * 0.2)),
        'lub_oil_pressure': np.random.uniform(0.8, 1.8, int(num_samples * 0.2)),
        'fuel_pressure': np.random.uniform(1.5, 2.0, int(num_samples * 0.2)),
        'coolant_pressure': np.random.uniform(0.5, 1.0, int(num_samples * 0.2)),
        'lub_oil_temp': np.random.uniform(105, 130, int(num_samples * 0.2)),
        'coolant_temp': np.random.uniform(95, 120, int(num_samples * 0.2)),
    }
    
    # Combine
    data = {}
    for key in normal_data:
        data[key] = np.concatenate([normal_data[key], failure_data[key]])
    
    # Create target variable (1 = failure likely, 0 = normal)
    data['engine_condition'] = [0] * len(normal_data['engine_rpm']) + [1] * len(failure_data['engine_rpm'])
    
    # Shuffle
    df = pd.DataFrame(data)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save to CSV
    df.to_csv('data/raw/engine_data.csv', index=False)
    print(f"✅ Data saved to data/raw/engine_data.csv")
    print(f"   Normal samples: {len(normal_data['engine_rpm'])}")
    print(f"   Failure samples: {len(failure_data['engine_rpm'])}")
    
    return df

def generate_sensor_stream(num_records=100):
    """Generate streaming sensor data"""
    print(f"Generating {num_records} streaming sensor records...")
    
    records = []
    base_time = datetime.now()
    
    for i in range(num_records):
        record_time = base_time - timedelta(minutes=i*5)
        
        # Simulate normal operation with occasional anomalies
        if random.random() < 0.9:  # 90% normal
            record = {
                "timestamp": record_time.isoformat(),
                "vehicle_id": f"VH{random.randint(1000, 9999)}",
                "engine_rpm": random.uniform(1500, 3000),
                "lub_oil_pressure": random.uniform(1.8, 2.5),
                "fuel_pressure": random.uniform(2.1, 2.6),
                "coolant_pressure": random.uniform(1.1, 1.5),
                "lub_oil_temp": random.uniform(85, 100),
                "coolant_temp": random.uniform(80, 95),
                "status": "normal"
            }
        else:  # 10% anomalies
            record = {
                "timestamp": record_time.isoformat(),
                "vehicle_id": f"VH{random.randint(1000, 9999)}",
                "engine_rpm": random.uniform(4000, 6500),
                "lub_oil_pressure": random.uniform(0.8, 1.5),
                "fuel_pressure": random.uniform(1.5, 2.0),
                "coolant_pressure": random.uniform(0.5, 1.0),
                "lub_oil_temp": random.uniform(105, 125),
                "coolant_temp": random.uniform(100, 115),
                "status": "warning"
            }
        
        records.append(record)
    
    # Save to JSON
    with open('data/raw/sensor_stream.json', 'w') as f:
        json.dump(records, f, indent=2)
    
    print(f"✅ Streaming data saved to data/raw/sensor_stream.json")
    return records

def generate_test_cases():
    """Generate test cases for API testing"""
    print("Generating API test cases...")
    
    test_cases = {
        "normal": {
            "engine_rpm": 2200,
            "lub_oil_pressure": 2.2,
            "fuel_pressure": 2.5,
            "coolant_pressure": 1.6,
            "lub_oil_temp": 85,
            "coolant_temp": 78
        },
        "warning": {
            "engine_rpm": 4200,
            "lub_oil_pressure": 1.5,
            "fuel_pressure": 2.0,
            "coolant_pressure": 1.0,
            "lub_oil_temp": 105,
            "coolant_temp": 98
        },
        "critical": {
            "engine_rpm": 6200,
            "lub_oil_pressure": 0.8,
            "fuel_pressure": 1.5,
            "coolant_pressure": 0.5,
            "lub_oil_temp": 125,
            "coolant_temp": 115
        },
        "edge_cases": [
            {
                "name": "high_rpm_normal_temp",
                "data": {
                    "engine_rpm": 6000,
                    "lub_oil_pressure": 2.0,
                    "fuel_pressure": 2.4,
                    "coolant_pressure": 1.4,
                    "lub_oil_temp": 90,
                    "coolant_temp": 85
                }
            },
            {
                "name": "normal_rpm_high_temp",
                "data": {
                    "engine_rpm": 2500,
                    "lub_oil_pressure": 1.2,
                    "fuel_pressure": 2.1,
                    "coolant_pressure": 1.1,
                    "lub_oil_temp": 120,
                    "coolant_temp": 110
                }
            }
        ]
    }
    
    with open('data/raw/test_cases.json', 'w') as f:
        json.dump(test_cases, f, indent=2)
    
    print(f"✅ Test cases saved to data/raw/test_cases.json")
    return test_cases

if __name__ == "__main__":
    print("🧪 Generating Test Data for ProactiveAI")
    print("="*50)
    
    # Create data directory if it doesn't exist
    import os
    os.makedirs('data/raw', exist_ok=True)
    
    # Generate all data
    engine_df = generate_engine_data(500)
    stream_data = generate_sensor_stream(50)
    test_cases = generate_test_cases()
    
    print("\n" + "="*50)
    print("✅ All test data generated successfully!")
    print("\n📁 Generated files:")
    print("  - data/raw/engine_data.csv (for training)")
    print("  - data/raw/sensor_stream.json (streaming data)")
    print("  - data/raw/test_cases.json (API test cases)")