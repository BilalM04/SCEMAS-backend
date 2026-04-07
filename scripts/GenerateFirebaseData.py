import os
import random
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# ------------------------
# INIT FIRESTORE
# ------------------------

load_dotenv()

cred_dict = {
    "type": os.environ["FIREBASE_TYPE"],
    "project_id": os.environ["FIREBASE_PROJECT_ID"],
    "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
    "private_key": os.environ["FIREBASE_PRIVATE_KEY"],
    "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
    "client_id": os.environ["FIREBASE_CLIENT_ID"],
    "auth_uri": os.environ["FIREBASE_AUTH_URI"],
    "token_uri": os.environ["FIREBASE_TOKEN_URI"],
    "auth_provider_x509_cert_url": os.environ["FIREBASE_AUTH_PROVIDER_X509_CERT_URL"],
    "client_x509_cert_url": os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
    "universe_domain": os.environ["FIREBASE_UNIVERSE_DOMAIN"]
}

cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()


# ------------------------
# CONSTANTS
# ------------------------

USERS = [
    ("OhbQwcer3SZ24X17W44naw0NEwh2", "user0@example.com"),
    ("RQyPt5AxGUSZCeEkBVQWs2mOyUf2", "user1@example.com"),
    ("Cv3m1Rj8J7hYnRFrw4Dz5zP7epP2", "user2@example.com"),
    ("e2nVuFT6SVatXgrzU3RIpVeVJ1h2", "user3@example.com"),
    ("rMYVkVyllZbCg0GgBfBn6Wn1Gwt1", "user4@example.com"),
    ("wMQLALkDhXRVzklX0mvj4Q8eWEj2", "user5@example.com"),
    ("hyEuX7YD6ZhF79wfNQXzphBjZ8p1", "user6@example.com"),
    ("F1CGuj8Rw1aIJmL8KEop9jC205m1", "user7@example.com"),
    ("jG942RqyMvcnKvTzwSyg4btI1OU2", "user8@example.com"),
    ("htnNPWJ3e0PkZfG4ZW3H4Dqc6zJ2", "user9@example.com"),
]

CITIES = {
    "Toronto": (43.65107, -79.347015),
    "Mississauga": (43.5890, -79.6441),
    "Brampton": (43.7315, -79.7624),
    "Hamilton": (43.2557, -79.8711),
    "Oakville": (43.4675, -79.6877),
    "Milton": (43.5183, -79.8774),
    "Burlington": (43.3255, -79.7990),
}

SENSOR_TYPES = ["temperature", "humidity", "noise", "air_quality"]
OPERATORS = ["greater_than", "less_than", "greater_or_equal", "less_or_equal"]
SEVERITIES = ["low", "medium", "high"]
STATUSES = ["active", "acknowledged", "resolved"]

# ------------------------
# HELPERS
# ------------------------

def random_timestamp():
    now = datetime.utcnow()
    past = now - timedelta(days=90)
    return int(random.uniform(past.timestamp(), now.timestamp()))

def random_location(city):
    lat, lon = CITIES[city]
    return {
        "latitude": lat + random.uniform(-0.05, 0.05),
        "longitude": lon + random.uniform(-0.05, 0.05),
    }

def random_measurement(sensor_type):
    if sensor_type == "temperature":
        return round(random.uniform(-10, 35), 2), "°C"
    elif sensor_type == "humidity":
        return round(random.uniform(20, 100), 2), "%"
    elif sensor_type == "noise":
        return round(random.uniform(30, 120), 2), "dB"
    else:
        return round(random.uniform(0, 300), 2), "AQI"

def gen_id(prefix):
    return f"{prefix}-{uuid.uuid4()}"

# ------------------------
# DELETE COLLECTION
# ------------------------

def delete_collection(collection_name, batch_size=400):
    print(f"🗑 Deleting collection: {collection_name}")
    col_ref = db.collection(collection_name)

    while True:
        docs = col_ref.limit(batch_size).stream()
        deleted = 0
        batch = db.batch()

        for doc in docs:
            batch.delete(doc.reference)
            deleted += 1

        if deleted == 0:
            break

        batch.commit()
        print(f"  deleted {deleted} docs")

    print(f"✅ Finished deleting {collection_name}\n")

# ------------------------
# MAIN
# ------------------------

def main():
    # ---- DELETE OLD DATA ----
    collections = ["alertrules", "alerts", "logs", "sensors", "subscriptions"]
    for col in collections:
        delete_collection(col)

    # ---- GENERATE + INSERT ----
    batch = db.batch()
    counter = 0
    BATCH_LIMIT = 450

    rules = []
    sensors = []

    # ALERT RULES
    for _ in range(10):
        user_id, _ = random.choice(USERS)
        city = random.choice(list(CITIES.keys()))
        ts = random_timestamp()

        rule_id = gen_id("rule")

        data = {
            "author_id": user_id,
            "created_at": ts,
            "updated_at": ts,
            "location": random_location(city),
            "name": f"{city.lower()}-{random.choice(SENSOR_TYPES)}-rule",
            "operator": random.choice(OPERATORS),
            "radius": random.randint(50, 500),
            "sensor_type": random.choice(SENSOR_TYPES),
            "threshold": round(random.uniform(10, 100), 2),
        }

        batch.set(db.collection("alertrules").document(rule_id), data)
        rules.append({"id": rule_id, **data})
        counter += 1

    # SENSORS
    for _ in range(75):
        city = random.choice(list(CITIES.keys()))
        sensor_type = random.choice(SENSOR_TYPES)
        measurement, unit = random_measurement(sensor_type)

        sensor_id = gen_id("sensor")

        data = {
            "city": city,
            "country": "Canada",
            "location": random_location(city),
            "measurement": measurement,
            "sensor_type": sensor_type,
            "time": random_timestamp(),
            "unit": unit,
        }

        batch.set(db.collection("sensors").document(sensor_id), data)
        sensors.append({"id": sensor_id, **data})
        counter += 1

        if counter >= BATCH_LIMIT:
            batch.commit()
            batch = db.batch()
            counter = 0

    # ALERTS
    for _ in range(10):
        rule = random.choice(rules)
        sensor = random.choice(sensors)

        alert_id = gen_id("alert")

        data = {
            "city": sensor["city"],
            "country": "Canada",
            "rule_id": rule["id"],
            "rule_name": rule["name"],
            "sensor_id": sensor["id"],
            "sensor_type": sensor["sensor_type"],
            "severity": random.choice(SEVERITIES),
            "status": random.choice(STATUSES),
            "time": random_timestamp(),
        }

        batch.set(db.collection("alerts").document(alert_id), data)
        counter += 1

    # LOGS
    for _ in range(50):
        user_id, email = random.choice(USERS)

        log_id = gen_id("log")

        data = {
            "user_id": user_id,
            "email": email,
            "log_message": f"Log event {random.randint(1000,9999)}",
            "time": random_timestamp(),
        }

        batch.set(db.collection("logs").document(log_id), data)
        counter += 1

    # SUBSCRIPTIONS
    for _ in range(30):
        rule = random.choice(rules)
        user_id, _ = random.choice(USERS)

        sub_id = gen_id("sub")

        data = {
            "rule_id": rule["id"],
            "rule_name": rule["name"],
            "subscriber_id": user_id,
        }

        batch.set(db.collection("subscriptions").document(sub_id), data)
        counter += 1

    # FINAL COMMIT
    if counter > 0:
        batch.commit()

    print("🚀 Fresh dataset loaded successfully!")

if __name__ == "__main__":
    main()