from flask_smorest import Blueprint
from models.ResponseSchemas import AggregatedResponseSchema, SensorDataSchema, SensorFilterSchema
from services.OperationalService import OperationalService
from services.SensorService import SensorService
from utils.Firebase import auth_required
from utils.Limiter import limiter

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
        pass


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


    return blp