from flask_smorest import Blueprint
from models.ResponseSchemas import AlertRuleSchema, AlertSchema, CreateAlertRuleSchema, SubscriptionSchema, SuccessResponseSchema, UpdateAlertSchema
from services.AlertService import AlertService
from services.OperationalService import OperationalService
from utils.Firebase import auth_required
from utils.Limiter import limiter

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
    @limiter.limit("60 per minute")
    @blp.response(200, AlertSchema(many=True))
    @auth_required(["admin", "operator"])
    def get_alerts():
        """Get all alerts (Admin & Operator)"""
        pass

    @blp.route("/<alert_id>")
    @limiter.limit("60 per minute")
    @blp.response(200, AlertSchema)
    @auth_required(["admin", "operator"])
    def get_alert(alert_id: str):
        """Get alert by ID (Admin & Operator)"""
        pass
    

    @blp.route("/update", methods=["PUT"])
    @limiter.limit("60 per minute")
    @blp.arguments(UpdateAlertSchema, location="query")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin", "operator"])
    def update_alert(data):
        """Update alert status and severity (Admin & Operator)"""
        pass
    

    @blp.route("/rules/create", methods=["POST"])
    @limiter.limit("60 per minute")
    @blp.arguments(CreateAlertRuleSchema, location="query")
    @blp.response(200, AlertRuleSchema)
    @auth_required(["admin"])
    def create_alert_rule(data):
        """Create a new alert rule (Admin only)"""
        pass
    

    @blp.route("/rules/delete/<rule_id>", methods=["DELETE"])
    @limiter.limit("60 per minute")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin"])
    def delete_alert_rule(rule_id):
        """Delete an alert rule (Admin only)"""
        pass
    

    @blp.route("/rules")
    @limiter.limit("60 per minute")
    @blp.response(200, AlertRuleSchema(many=True))
    @auth_required(["admin"])
    def get_all_alert_rules():
        """Get all alert rules (Admin Only)"""
        pass

    @blp.route("/rules/<rule_id>")
    @limiter.limit("60 per minute")
    @blp.response(200, AlertRuleSchema)
    @auth_required(["admin"])
    def get_alert_rule():
        """Get all alert rules (Admin Only)"""
        pass
    

    @blp.route("/subscribe/<rule_id>", methods=["POST"])
    @limiter.limit("60 per minute")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin", "operator", "public"])
    def subscribe_to_alert(rule_id):
        """Subscribe to an alert rule (Admin, Operator, & Public)"""
        pass


    @blp.route("/unsubscribe/<rule_id>", methods=["DELETE"])
    @limiter.limit("60 per minute")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin", "operator", "public"])
    def unsubscribe_from_alert(rule_id):
        """Unsubscribe from an alert rule (Admin, Operator, & Public)"""
        pass

    @blp.route("/subscriptions", methods=["GET"])
    @limiter.limit("60 per minute")
    @blp.response(200, SubscriptionSchema(many=True))
    @auth_required(["admin", "operator", "public"])
    def get_my_subscriptions():
        """Get subscriptions for the authenticated user (Admin, Operator, & Public)"""


    return blp