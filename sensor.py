import time
import random
import requests
import pyrebase
import os
from models.SensorType import SensorType

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyC_TkdChDZ7ipH3rTZN4B4-R8P2ewoWavE",
    "authDomain": "scemas-42be0.firebaseapp.com",
    "projectId": "scemas-42be0.firebasestorage.app",
    "storageBucket": "467209699711",
    "messagingSenderId": "1:467209699711:web:d742ffaecfa35c4bf21a4a",
    "appId": "1:467209699711:web:d742ffaecfa35c4bf21a4a",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Backend URL
backend_url = "http://127.0.0.1:5000/sensors/ingest"

# Sensor data generator
def generate_sensor_data(sensor_type, city, country, longitude, latitude):

    measurement = 0
    units = ""
    if (sensor_type == SensorType.TEMPERATURE):
        measurement = random.randint(-20,20)
        units = "°C"
    elif (sensor_type == SensorType.HUMIDITY):
        measurement = random.randint(0,100)
        units = "%"
    elif (sensor_type == SensorType.AIR_QUALITY):
        measurement = random.randint(0,500)
        units = "AQI"
    elif (sensor_type == SensorType.NOISE):
        measurement = random.randint(30,120)
        units = "dB"
       

    return {
        "measurement": measurement,
        "unit": units,
        "time": int(time.time()),
        "location": {"latitude": latitude, "longitude": longitude},
        "sensor_type": sensor_type.value,
        "country": country,
        "city": city
    }

# Sign up and get token
def signup(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user["idToken"]
    except Exception as e:
        print(f"Sign up failed: {e}")
        return None

# Authenticate and get token
def authenticate(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user["idToken"]
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

# Send sensor data to backend
def send_sensor_data(token, data):
    headers = {"Authorization": f"Bearer {token}"}
    print("sending data")
    print(data["sensor_type"])
    print(data)
    response = requests.put( backend_url, json=data, headers=headers )

    if response.status_code == 200:
        print("Sensor data sent successfully.")
    else:
        print(f"Failed to send sensor data: {response.status_code}, {response.text}")

# Main loop
def main():
    email = "sensor@email.com"
    password = "sensor123"
    token = authenticate(email, password)

    if not token:
        token = signup(email, password)
        if not token:
            print("Exiting due to authentication failure.")
            return

    while True:
        cities = [
            {"city": "Toronto", "country": "Canada", "latitude": 43.6532, "longitude": -79.3832},
            {"city": "Vancouver", "country": "Canada", "latitude": 49.2827, "longitude": -123.1207},
            {"city": "Mississauga", "country": "Canada", "latitude": 43.5890, "longitude": -79.6441},
            {"city": "Brampton", "country": "Canada", "latitude": 43.7315, "longitude": -79.7624},
            {"city": "Markham", "country": "Canada", "latitude": 43.8561, "longitude": -79.3370},
        ]
        for city in cities:
            for sensor_type in SensorType:
                sensor_data = generate_sensor_data(sensor_type, city["city"], city["country"], city["longitude"], city["latitude"])
                send_sensor_data(token, sensor_data)
        time.sleep(600)  # Wait for 5 minutes

if __name__ == "__main__":
    main()