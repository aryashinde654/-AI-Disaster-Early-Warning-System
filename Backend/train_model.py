import pandas as pd
import numpy as np
import joblib
import requests
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

# Constants
DATA_PATH = "C:/Users/ARYA SHINDE/OneDrive/Desktop/AI Disaster Early Warning System/Backend/data.csv"
MODEL_PATH = "C:/Users/ARYA SHINDE/OneDrive/Desktop/AI Disaster Early Warning System/Backend/ml_model.pkl"
USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
OPENCAGE_API_KEY = "5610732233684fb88881c7450c47e451"  # Replace with your key
OPENCAGE_URL = "https://api.opencagedata.com/geocode/v1/json"

def fetch_live_earthquake_data():
    """
    Fetch real-time earthquake data from USGS API.
    Returns: DataFrame containing magnitude, latitude, longitude, depth, and location.
    """
    try:
        print("🌍 Fetching live earthquake data...")
        response = requests.get(USGS_API_URL)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        
        earthquakes = []
        for quake in data.get('features', []):
            properties = quake.get('properties', {})
            geometry = quake.get('geometry', {})
            
            if geometry and properties.get('mag') is not None:
                earthquakes.append([
                    properties['mag'],  # Magnitude
                    geometry['coordinates'][1],  # Latitude
                    geometry['coordinates'][0],  # Longitude
                    geometry['coordinates'][2],  # Depth
                    properties.get('place', 'Unknown')  # Location
                ])

        df = pd.DataFrame(earthquakes, columns=["magnitude", "latitude", "longitude", "depth", "location"])
        df["risk_level"] = np.random.choice([0, 1, 2], size=len(df))  # Assign random risk level (to be improved)
        print("✅ Live data fetched successfully!")
        return df
    except requests.RequestException as e:
        print(f"⚠️ Error fetching live data: {e}")
        return None

def load_data():
    """
    Load and preprocess disaster dataset.
    Returns: Processed DataFrame or None if loading fails.
    """
    try:
        print("📂 Loading local dataset...")
        df = pd.read_csv(DATA_PATH)
        required_columns = {"latitude", "longitude", "depth", "magnitude", "risk_level"}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Missing required columns: {required_columns - set(df.columns)}")
        
        df.dropna(inplace=True)  # Remove missing values
        risk_mapping = {"Low": 0, "Medium": 1, "High": 2}
        df["risk_level"] = df["risk_level"].map(risk_mapping)
        
        print("✅ Local dataset loaded successfully!")
        return df
    except Exception as e:
        print(f"⚠️ Error loading data: {e}")
        return None

def train_model(df):
    """
    Train a machine learning model to predict disaster risk levels.
    Saves the trained model to disk.
    """
    try:
        print("🚀 Training AI Model...")
        X = df[["latitude", "longitude", "depth", "magnitude"]]
        y = df["risk_level"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", XGBClassifier(n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42))
        ])
        
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        
        print("✅ Model Training Complete!")
        print(f"🎯 Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print("📊 Classification Report:\n", classification_report(y_test, y_pred))
        
        joblib.dump(pipeline, MODEL_PATH)
        print(f"💾 Model saved successfully at {MODEL_PATH}")
    except Exception as e:
        print(f"⚠️ Error training model: {e}")

if __name__ == "__main__":
    print("🚀 Starting Disaster Model Training...")

    # Load local dataset
    dataset = load_data()

    # Fetch real-time earthquake data
    live_data = fetch_live_earthquake_data()

    if dataset is not None and live_data is not None:
        # Merge local & live data
        combined_data = pd.concat([dataset, live_data], ignore_index=True)
        print(f"📊 Combined dataset size: {combined_data.shape}")

        # Train AI model
        train_model(combined_data)
    else:
        print("⚠️ Training aborted due to data issues.")

def reverse_geocode(lat, lon):
    """Get location name from latitude & longitude using OpenCage API"""
    try:
        params = {"q": f"{lat},{lon}", "key": OPENCAGE_API_KEY}
        response = requests.get(OPENCAGE_URL, params=params)
        data = response.json()
        return data["results"][0]["formatted"] if data["results"] else "Unknown Location"
    except Exception as e:
        print(f"⚠️ Geocoding Error: {e}")
        return "Unknown Location"

def fetch_live_earthquake_data():
    """Fetch real-time earthquake data and add location names"""
    USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    
    try:
        response = requests.get(USGS_API_URL)
        data = response.json()
        
        earthquakes = []
        for quake in data.get("features", []):
            props = quake.get("properties", {})
            geom = quake.get("geometry", {})

            if geom and props.get("mag") is not None:
                lat, lon, depth = geom["coordinates"][1], geom["coordinates"][0], geom["coordinates"][2]
                location = reverse_geocode(lat, lon)  # Get readable location

                earthquakes.append({
                    "magnitude": props["mag"],
                    "latitude": lat,
                    "longitude": lon,
                    "depth": depth,
                    "risk_level": 2 if props["mag"] >= 6 else (1 if props["mag"] >= 4 else 0),
                    "location": location
                })

        return {"earthquakes": earthquakes}
    except Exception as e:
        print(f"⚠️ Error fetching live data: {e}")
        return None