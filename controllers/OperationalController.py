from flask_smorest import Blueprint
from models.ResponseSchemas import LogSchema, SystemHealthSchema
from services.OperationalService import OperationalService
from utils.Firebase import auth_required
from utils.Limiter import limiter
from dataclasses import asdict

def create_operational_blueprint(operational_service: OperationalService):
    blp = Blueprint(
        "operations",
        "operations",
        url_prefix="/operations",
        description="Operational endpoints"
    )

    @blp.route("/logs")
    @limiter.limit("60 per minute")
    @blp.response(200, LogSchema(many=True))
    @auth_required(["admin"])
    def get_logs():
        logs = operational_service.get_all_logs()
        return [asdict(log) for log in logs]
    
    @blp.route("/health")
    @limiter.limit("60 per minute")
    @blp.response(200, SystemHealthSchema)
    @auth_required(["admin", "operator"])
    def get_system_health():
        return asdict(operational_service.get_system_health())

    return blp