from flask_smorest import Blueprint
from models.ResponseSchemas import LogSchema, SystemHealthSchema
from services.OperationalService import OperationalService
from utils.Firebase import auth_required
from utils.Limiter import limiter

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
        """Get system logs (Admin only)"""
        return operational_service.get_all_logs()
    
    @blp.route("/health")
    @limiter.limit("60 per minute")
    @blp.response(200, SystemHealthSchema)
    @auth_required(["admin", "operator"])
    def get_system_health():
        """Get system health metrics (Admin & Operator)"""
        return operational_service.get_system_health()

    return blp