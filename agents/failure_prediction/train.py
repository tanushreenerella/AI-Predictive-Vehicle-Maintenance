import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

# Create directory if it doesn't exist
os.makedirs("agents/failure_prediction", exist_ok=True)

def train_model():
    try:
        # Load dataset
        print("Loading dataset...")
        data = pd.read_csv("data/raw/engine_data.csv")
        
        # Clean column names
        data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_")
        
        # Check if target column exists
        if "engine_condition" not in data.columns:
            # Create synthetic target for demo
            np.random.seed(42)
            data["engine_condition"] = np.random.choice([0, 1], size=len(data), p=[0.8, 0.2])
            print("⚠️ Created synthetic target column for demo")
        
        # Split features & target
        X = data.drop("engine_condition", axis=1)
        y = data["engine_condition"]
        
        # Ensure we have the right columns
        expected_columns = [
            "engine_rpm", "lub_oil_pressure", "fuel_pressure", 
            "coolant_pressure", "lub_oil_temp", "coolant_temp"
        ]
        
        for col in expected_columns:
            if col not in X.columns:
                X[col] = np.random.normal(0, 1, len(X))
                print(f"⚠️ Added synthetic column: {col}")
        
        X = X[expected_columns]  # Ensure correct order
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        print("Training model...")
        model = XGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            eval_metric="logloss",
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        preds = model.predict(X_test)
        accuracy = accuracy_score(y_test, preds)
        print(f"✅ Model trained successfully")
        print(f"Accuracy: {accuracy:.2%}")
        print(f"Class distribution:\n{y.value_counts(normalize=True)}")
        print("\nClassification Report:")
        print(classification_report(y_test, preds))
        
        # Save model & scaler using pickle (more stable than joblib across versions)
        with open("agents/failure_prediction/model.pkl", "wb") as f:
            pickle.dump(model, f)
        
        with open("agents/failure_prediction/scaler.pkl", "wb") as f:
            pickle.dump(scaler, f)
        
        # Save feature names
        with open("agents/failure_prediction/features.pkl", "wb") as f:
            pickle.dump(expected_columns, f)
            
        print("✅ Model artifacts saved successfully")
        
    except Exception as e:
        print(f"❌ Error during training: {e}")
        raise

if __name__ == "__main__":
    train_model()