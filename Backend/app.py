from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os
import requests  # Required for OpenCage API
from twilio.rest import Client

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Load pre-trained ML model for Earthquakes
MODEL_PATH = "ml_model.pkl"
try:
    model = joblib.load(MODEL_PATH)
    print("✅ ML Model Loaded Successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None  # Handle missing model case

# Twilio API Credentials (Secure with environment variables)
TWILIO_ACCOUNT_SID = os.getenv("AC145885ba0f2b0f5f8912af2aecd3e3f8")
TWILIO_AUTH_TOKEN = os.getenv("9ee0be08348193587c97d95dd10288f1")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+19592084629")  # Default fallback
USER_PHONE_NUMBER = os.getenv("USER_PHONE_NUMBER", "+918087048705")  # Default fallback

def send_sms_alert(message):
    """Send an SMS alert using Twilio API."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("⚠️ Twilio credentials missing! SMS not sent.")
        return
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=USER_PHONE_NUMBER
        )
        print("📩 SMS Alert Sent Successfully!")
    except Exception as e:
        print(f"⚠️ Error sending SMS: {e}")

def get_location_name(lat, lon):
    """Fetch location name using OpenCage API."""
    OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY", "5610732233684fb88881c7450c47e451")  # Use env variable with fallback

    if not OPENCAGE_API_KEY:
        print("⚠️ OpenCage API Key is missing!")
        return "Unknown Location"

    try:
        url = f"https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key={OPENCAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        print("🔍 OpenCage API Response:", data)  # Debugging

        if "results" in data and data["results"]:
            return data["results"][0].get("formatted", "Unknown Location")
        return "Unknown Location"

    except Exception as e:
        print(f"⚠️ Error fetching location name: {e}")
        return "Unknown Location"


@app.route("/predict_earthquake", methods=["POST"])
def predict_earthquake():
    """Predict earthquake risk using ML model."""
    if model is None:
        return jsonify({"error": "ML model not loaded"}), 500

    try:
        data = request.get_json()
        required_keys = ["latitude", "longitude", "depth", "magnitude"]

        if not all(key in data for key in required_keys):
            return jsonify({"error": "Missing required parameters"}), 400

        try:
            features = np.array([[float(data[key]) for key in required_keys]])
        except ValueError:
            return jsonify({"error": "Invalid input data format"}), 400

        prediction = model.predict(features)[0]
        risk_labels = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}
        risk_level = risk_labels.get(prediction, "Unknown Risk")

        # Get location name
        location_name = get_location_name(data["latitude"], data["longitude"])

        print(f"🔍 Predicted Earthquake Risk Level: {risk_level} at {location_name}")  # Debugging log

        if prediction == 2:
            send_sms_alert(f"🚨 High-risk earthquake detected in {location_name}! Stay safe.")

        return jsonify({"risk_level": risk_level, "prediction": int(prediction), "location": location_name})

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route("/predict_flood", methods=["POST"])
def predict_flood():
    """Predicts flood risk based on rainfall and river level."""
    try:
        data = request.get_json()
        required_keys = ["latitude", "longitude", "rainfall", "riverLevel"]

        if not all(key in data for key in required_keys):
            return jsonify({"error": "Missing required parameters"}), 400

        try:
            rainfall = float(data["rainfall"])
            river_level = float(data["riverLevel"])
        except ValueError:
            return jsonify({"error": "Invalid input data format"}), 400

        # Improved risk conditions
        if rainfall > 100 and river_level > 5:
            risk_level = "High Risk"
        elif rainfall > 50 or river_level > 3:
            risk_level = "Medium Risk"
        else:
            risk_level = "Low Risk"

        # Get location name
        location_name = get_location_name(data["latitude"], data["longitude"])

        print(f"🔍 Predicted Flood Risk Level: {risk_level} at {location_name}")  # Debugging log

        if risk_level == "High Risk":
            send_sms_alert(f"🚨 High flood risk detected in {location_name}! Stay alert.")

        return jsonify({"risk_level": risk_level, "location": location_name})

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route("/predict_wildfire", methods=["POST"])
def predict_wildfire():
    """Predicts wildfire risk based on temperature and wind speed."""
    try:
        data = request.get_json()
        required_keys = ["latitude", "longitude", "temperature", "windSpeed"]

        if not all(key in data for key in required_keys):
            return jsonify({"error": "Missing required parameters"}), 400

        try:
            temperature = float(data["temperature"])
            wind_speed = float(data["windSpeed"])
        except ValueError:
            return jsonify({"error": "Invalid input data format"}), 400

        # Improved risk conditions
        if temperature > 45 or wind_speed > 60:
            risk_level = "High Risk"
        elif temperature > 35 or wind_speed > 40:
            risk_level = "Medium Risk"
        else:
            risk_level = "Low Risk"

        # Get location name
        location_name = get_location_name(data["latitude"], data["longitude"])

        print(f"🔍 Predicted Wildfire Risk Level: {risk_level} at {location_name}")  # Debugging log

        if risk_level == "High Risk":
            send_sms_alert(f"🚨 High wildfire risk detected in {location_name}! Stay safe.")

        return jsonify({"risk_level": risk_level, "location": location_name})

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "AI Disaster Early Warning System API is running!"})

if __name__ == "__main__":
    DEBUG_MODE = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=DEBUG_MODE, host="0.0.0.0", port=5000)
