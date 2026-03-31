from flask_smorest import Blueprint
from models.ResponseSchemas import AlertRuleSchema, AlertSchema, CreateAlertRuleSchema, SuccessResponseSchema, UpdateAlertSchema
from services.AlertService import AlertService
from services.OperationalService import OperationalService
from utils.firebase import auth_required

def create_alerts_blueprint(
    alert_service: AlertService,
    operational_service: OperationalService
):
    blp = Blueprint(
        "alerts",
        "alerts",
        url_prefix="/alerts",
        description="Alert endpoints"
    )

    @blp.route("/")
    @blp.response(200, AlertSchema(many=True))
    @auth_required(["admin", "operator"])
    def get_alerts():
        """Get all alerts (Admin & Operator)"""
        pass
    

    @blp.route("/update", methods=["PUT"])
    @blp.arguments(UpdateAlertSchema, location="query")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin", "operator"])
    def update_alert(data):
        """Update alert status and severity (Admin & Operator)"""
        pass
    

    @blp.route("/rules/create", methods=["POST"])
    @blp.arguments(CreateAlertRuleSchema, location="query")
    @blp.response(200, AlertRuleSchema)
    @auth_required(["admin"])
    def create_alert_rule(data):
        """Create a new alert rule (Admin only)"""
        pass
    

    @blp.route("/rules/delete/<rule_id>", methods=["DELETE"])
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin"])
    def delete_alert_rule(rule_id):
        """Delete an alert rule (Admin only)"""
        pass
    

    @blp.route("/rules")
    @blp.response(200, AlertRuleSchema(many=True))
    @auth_required(["admin"])
    def get_all_alert_rules():
        """Get all alert rules (Admin Only)"""
        pass
    

    @blp.route("/subscribe/<rule_id>", methods=["POST"])
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin", "operator", "public"])
    def subscribe_to_alert(rule_id):
        """Subscribe to an alert rule (Admin, Operator, & Public)"""
        pass


    @blp.route("/unsubscribe/<rule_id>", methods=["DELETE"])
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin", "operator", "public"])
    def unsubscribe_from_alert(rule_id):
        """Unsubscribe from an alert rule (Admin, Operator, & Public)"""
        pass


    return blp