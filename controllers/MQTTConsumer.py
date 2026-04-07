import paho.mqtt.client as mqtt
import ssl
import json
import os
from marshmallow import ValidationError
from firebase_admin import auth

from services.SensorService import SensorService
from services.OperationalService import OperationalService
from services.AlertService import AlertService
from models.ResponseSchemas import SensorDataSchema
from controllers.SensorController import ingest_sensor_data

class MQTTConsumer:
    def __init__(self, sensor_service: SensorService, operational_service: OperationalService, alert_service: AlertService,):
        self.sensor_service = sensor_service
        self.operational_service = operational_service
        self.alert_service = alert_service

        self.client = mqtt.Client()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.client.tls_set(ca_certs=os.path.join(BASE_DIR, "AmazonRootCA1.pem"), 
                   certfile=os.path.join(BASE_DIR, "backend-certificate.pem.crt"), 
                   keyfile=os.path.join(BASE_DIR, "backend-private.pem.key"),)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def start(self):
        # connect to MQTT broker (MQTTS)
        # self.client.connect("localhost", 1883) --> for dev without TLS
        self.client.connect("a3h9uwntq5s16k-ats.iot.us-east-2.amazonaws.com", 8883)
        self.client.loop_forever()
    
    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker:", rc)

        # Subscribe to telemetry topic
        client.subscribe("sensor/device/telemetry")

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from MQTT broker:", rc)

    def on_message(self, client, userdata, msg):
        print("got message")
        try:
            payload = json.loads(msg.payload.decode())

            token = payload.get("token")
            data = payload.get("data")

            if not token or not data:
                raise ValueError("Missing token or data")

            # 🔐 Authenticate using Firebase
            decoded = auth.verify_id_token(token)
            print(decoded)

            # ✅ Validate schema
            schema = SensorDataSchema()
            validated = schema.load(data)
            print(validated)

            # ✅ Use SensorController ingestion logic
            ingest_sensor_data(self.sensor_service, self.operational_service, self.alert_service, validated)

            print("✅ MQTT ingestion success")

        except ValidationError as ve:
            print("❌ Schema validation failed:", ve.messages)

        except Exception as e:
            print("❌ MQTT processing error:", e)