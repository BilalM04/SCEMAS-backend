from flask_smorest import Blueprint
from models.ResponseSchemas import AggregatedResponseSchema, SensorDataSchema, SensorFilterSchema, SuccessResponseSchema
from services.OperationalService import OperationalService
from services.SensorService import SensorService
from utils.Firebase import auth_required
from utils.Limiter import limiter
from models.Coordinate import Coordinate
from models.SensorType import SensorType

def create_sensors_blueprint(
    sensor_service: SensorService,
    operational_service: OperationalService
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
        return sensor_service.get_all_sensor_data()



    @blp.route("/<sensor_id>")
    @limiter.limit("60 per minute")
    @blp.response(200, SensorDataSchema)
    @auth_required(["admin", "operator"])
    def get_sensor_data_by_id(sensor_id: str):
        """Get sensor data by id (Admin & Operator)"""
        pass


    @blp.route("/aggregated")
    @limiter.limit("60 per minute")
    @blp.arguments(SensorFilterSchema, location="query")
    @blp.response(200, AggregatedResponseSchema)
    @auth_required(["admin", "operator", "public"])
    def get_aggregated_data(args):
        """
        Get aggregated sensor data (An, Operator, & Public)

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
        return {"data" : sensor_service.get_aggregated_data(sensor_type, city, country, start_time, end_time)}


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
        pass

    #temporary path
    @blp.route("/delete/<sensor_id>")
    @blp.response(200, SensorDataSchema)
    @auth_required(["admin", "operator"])
    def delete_sensor_data_by_id(sensor_id: str):
        """Get sensor data by id (Testing only)"""
        try:
            sensor_service.delete_sensor_data(sensor_id)
            return {"success": True}
        except Exception as e:
            print(f"Error occurred while ingesting sensor data: {e}")
            return {"success": False, "error": str(e)}, 500
        pass

    @blp.route("/ingest", methods=["PUT"])
    @blp.arguments(SensorDataSchema)
    @blp.response(200, SuccessResponseSchema)
    def ingest_sensor_data(args):
        """Ingest sensor data (Admin & Operator)"""
        try: 

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
                
            sensor_service.save_sensor_data(
                measurement=measurement,
                unit=units,
                time=args["time"],
                location=Coordinate(latitude=args["location"]["latitude"], longitude=args["location"]["longitude"]),
                sensor_type=sensor_type,
                country=args["country"],
                city=args["city"]
            )
            return {"success": True, "message": "Sensor data ingested successfully."}
        except Exception as e:
            print(f"Error occurred while ingesting sensor data: {e}")
            return {"success": False, "error": str(e)}, 500


    return blp