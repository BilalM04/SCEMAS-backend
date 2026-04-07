from dataclasses import asdict
import random
from flask import request
from flask_smorest import Blueprint
from models.ResponseSchemas import AggregatedResponseSchema, SensorDataSchema, SensorFilterSchema, SuccessResponseSchema, SensorPredictionSchema, PredictionResponseSchema
from services.OperationalService import OperationalService
from services.SensorService import SensorService
from utils.Firebase import auth_required
from utils.Limiter import limiter
from models.Coordinate import Coordinate
from models.SensorType import SensorType
from services.AlertService import AlertService

def create_sensors_blueprint(
    sensor_service: SensorService,
    operational_service: OperationalService,
    alert_service: AlertService
):
    blp = Blueprint(
        "sensors",
        "sensors",
        url_prefix="/sensors",
        description="Sensor endpoints"
    )

    @blp.route("/")
    @limiter.limit("60 per minute")
    @blp.response(200, SensorDataSchema(many=True))
    @auth_required(["admin", "operator"])
    def get_sensor_data():
        """Get all sensor data (Admin & Operator)"""
        data = sensor_service.get_all_sensor_data()
        return [d.to_dict() for d in data]



    @blp.route("/<sensor_id>")
    @limiter.limit("60 per minute")
    @blp.response(200, SensorDataSchema)
    @auth_required(["admin", "operator"])
    def get_sensor_data_by_id(sensor_id: str):
        """Get sensor data by ID (Admin & Operator)"""
        data = sensor_service.get_sensor_data_by_id(sensor_id)
        return data.to_dict()


    @blp.route("/aggregated")
    @limiter.limit("60 per minute")
    @blp.arguments(SensorFilterSchema, location="query")
    @blp.response(200, AggregatedResponseSchema)
    @auth_required(["admin", "operator", "public"])
    def get_aggregated_data(args):
        """
        Get aggregated sensor data (Admin, Operator, & Public)

        Optional filters:
        - country
        - city
        - sensor_type
        - start_time
        - end_time
        """
        sensor_type = None
        country = None
        city = None  
        start_time = None
        end_time = None
        if "sensor_type" in args:
            sensor_type = SensorType(args["sensor_type"])
        if "country" in args:
            country = args["country"]
        if "city" in args:
            city = args["city"]
        if "start_time" in args:
            start_time = args["start_time"]
        if "end_time" in args:
            end_time = args["end_time"]
        
        print(f"Received request for aggregated data with filters - sensor_type: {sensor_type}, city: {city}, country: {country}, start_time: {start_time}, end_time: {end_time}")
        raw = sensor_service.get_aggregated_data(sensor_type, city, country, start_time, end_time)
        converted = {
            st.value: data
            for st, data in raw.items()
        }
        return {"data": converted}


    @blp.route("/filter")
    @limiter.limit("60 per minute")
    @blp.arguments(SensorFilterSchema, location="query")
    @blp.response(200, SensorDataSchema(many=True))
    @auth_required(["admin", "operator"])
    def get_filtered_sensor_data(args):
        """
        Get filtered sensor data (Admin & Operator)

        Optional filters:
        - country
        - city
        - sensor_type
        - start_time
        - end_time
        """
        sensor_type = None
        country = None
        city = None  
        start_time = None
        end_time = None
        if "sensor_type" in args:
            sensor_type = SensorType(args["sensor_type"])
        if "country" in args:
            country = args["country"]
        if "city" in args:
            city = args["city"]
        if "start_time" in args:
            start_time = args["start_time"]
        if "end_time" in args:
            end_time = args["end_time"]
        
        data = sensor_service.get_filtered_sensor_data(sensor_type, city, country, start_time, end_time)
        return [d.to_dict() for d in data]

    @blp.route("/ingest", methods=["PUT"])
    @blp.arguments(SensorDataSchema)
    @blp.response(200, SuccessResponseSchema)
    def ingest_sensor_data(args):
        """Ingest sensor data (Sensor only)"""
        try: 
            user = request.user
            sensor_type = args["sensor_type"]
            measurement = args["measurement"]
            units = args["unit"]
            if (sensor_type == SensorType.TEMPERATURE):
                if measurement < -20 or measurement > 20:
                    raise ValueError("Temperature measurement out of range (-20 to 20 °C)")
                if units != "°C":
                    raise ValueError("Invalid unit for temperature sensor. Expected '°C'.")
            elif (sensor_type == SensorType.HUMIDITY):
                if measurement < 0 or measurement > 100:
                    raise ValueError("Humidity measurement out of range (0 to 100 %)")
                if units != "%":
                    raise ValueError("Invalid unit for humidity sensor. Expected '%'.")
            elif (sensor_type == SensorType.AIR_QUALITY):
                if measurement < 0 or measurement > 500:
                    raise ValueError("Air quality measurement out of range (0 to 500 AQI)")
                if units != "AQI":
                    raise ValueError("Invalid unit for air quality sensor. Expected 'AQI'.")
            elif (sensor_type == SensorType.NOISE):
                if measurement < 30 or measurement > 120:
                    raise ValueError("Noise measurement out of range (30 to 120 dB)")
                if units != "dB":
                    raise ValueError("Invalid unit for noise sensor. Expected 'dB'.")
                
            sensor = sensor_service.save_sensor_data(
                measurement=measurement,
                unit=units,
                time=args["time"],
                location=Coordinate(latitude=args["location"]["latitude"], longitude=args["location"]["longitude"]),
                sensor_type=sensor_type,
                country=args["country"],
                city=args["city"]
            )

            operational_service.log_event(user["uid"], f"Ingesting {sensor_type} sensor data from {asdict(sensor.location)}", user.get("email", ""))

            alert_service.evaluate_sensor_data(
                sensor.sensor_id, 
                sensor.sensor_type, 
                sensor.measurement, 
                sensor.location, 
                sensor.timestamp, 
                sensor.country, 
                sensor.city, 
            )

            return {"success": True, "message": "Sensor data ingested successfully."}
        except Exception as e:
            print(f"Error occurred while ingesting sensor data: {e}")
            return {"success": False, "error": str(e)}, 500


    @blp.route("/predict")
    @blp.arguments(SensorPredictionSchema, location="query")
    @blp.response(200, PredictionResponseSchema)
    @auth_required(["admin", "operator", "public"])
    def predict_sensor_data(args):
        """
        Predict sensor data for the next 30 days
        Optional filters:
        - country
        - city
        - sensor_type
        """
        country = args["country"]
        city = args["city"]
        sensor_type = args["sensor_type"]

        # getting filtered sensor data based no the location and enviromental metric that was asked for. 
        past_data = sensor_service.get_filtered_sensor_data(
            sensor_type=SensorType(sensor_type),
            city=city,
            country=country
        )

        # Sort by time descending
        past_data = sorted(past_data, key=lambda s: s.time, reverse=True)

        # If there is not enough data to make a prediction, return empty response
        if len(past_data) < 5: 
            return {
                "sensor_type": sensor_type,
                "country": country,
                "city": city,
                "predictions": [],
                "average_of_last_5": None
            }

        # Predict the next 30 days based on average of last 5 measurements with random variation
        last_5 = past_data[:5]
        avg_measurement = sum(s.measurement for s in last_5) / 5

        # Generate 30 predicted values with a minor variation around average to simulate realistic weather patterns
        predictions = []
        for _ in range(30):
            variation = random.uniform(-0.1 * avg_measurement, 0.1 * avg_measurement)  # ±10% variation
            predictions.append(round(avg_measurement + variation, 2))


        return {
            "sensor_type": sensor_type,
            "country": country,
            "city": city,
            "predictions": predictions,
            "average_of_last_5": round(avg_measurement, 2)
        }


    return blp