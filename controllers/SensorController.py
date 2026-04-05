from flask_smorest import Blueprint
from models.ResponseSchemas import AggregatedResponseSchema, SensorDataSchema, SensorFilterSchema, SuccessResponseSchema
from services.OperationalService import OperationalService
from services.SensorService import SensorService
from utils.Firebase import auth_required
from utils.Limiter import limiter
from models.Coordinate import Coordinate

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
        Get aggregated sensor data (Admin, Operator, & Public)

        Optional filters:
        - country
        - city
        - sensor_type
        - start_time
        - end_time
        """
        pass


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

    @blp.route("/ingest", methods=["PUT"])
    @blp.arguments(SensorDataSchema)
    @blp.response(200, SuccessResponseSchema)
    def ingest_sensor_data(args):
        """Ingest sensor data (Admin & Operator)"""
        try: 
            sensor_service.save_sensor_data(
                sensor_id=args["sensor_id"],
                measurement=args["measurement"],
                unit=args["unit"],
                time=args["time"],
                location=Coordinate(lat=args["location"]["lat"], lon=args["location"]["lon"]),
                sensor_type=args["sensor_type"],
                country=args["country"],
                city=args["city"]
            )
            return {"success": True, "message": "Sensor data ingested successfully."}
        except Exception as e:
            print(f"Error occurred while ingesting sensor data: {e}")
            return {"success": False, "error": str(e)}, 500


    return blp