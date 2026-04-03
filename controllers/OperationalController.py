from flask_smorest import Blueprint
from models.ResponseSchemas import LogSchema, SystemHealthSchema
from services.OperationalService import OperationalService
from utils.Firebase import auth_required

def create_operational_blueprint(operational_service: OperationalService):
    blp = Blueprint(
        "operations",
        "operations",
        url_prefix="/operations",
        description="Operational endpoints"
    )

    @blp.route("/logs")
    @blp.response(200, LogSchema(many=True))
    @auth_required(["admin"])
    def get_logs():
        """Get system logs (Admin only)"""
        pass
    
    @blp.route("/health")
    @blp.response(200, SystemHealthSchema)
    @auth_required(["admin", "operator"])
    def get_system_health():
        """Get system health metrics (Admin & Operator)"""
        pass

    return blp