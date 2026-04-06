# controllers/AlertController.py  (replace the stub bodies)
from flask import request
from flask_smorest import Blueprint, abort
from models.AlertSeverity import AlertSeverity
from models.AlertStatus import AlertStatus
from models.ComparisonOperator import ComparisonOperator
from models.Coordinate import Coordinate
from models.SensorType import SensorType
from models.ResponseSchemas import (
    AlertRuleSchema, AlertSchema, CreateAlertRuleSchema,
    SubscriptionSchema, SuccessResponseSchema, UpdateAlertSchema,
)
from services.AlertService import AlertService
from services.OperationalService import OperationalService
from utils.Firebase import auth_required
from utils.Limiter import limiter


def create_alerts_blueprint(
    alert_service: AlertService,
    operational_service: OperationalService,
):
    blp = Blueprint("alerts", "alerts", url_prefix="/alerts",
                    description="Alert endpoints")

    @blp.route("/")
    @limiter.limit("60 per minute")
    @blp.response(200, AlertSchema(many=True))
    @auth_required(["admin", "operator"])
    def get_alerts():
        """Get all alerts (Admin & Operator)"""
        return alert_service.get_all_alerts()

    @blp.route("/<alert_id>")
    @limiter.limit("60 per minute")
    @blp.response(200, AlertSchema)
    @auth_required(["admin", "operator"])
    def get_alert(alert_id: str):
        """Get alert by ID (Admin & Operator)"""
        alert = alert_service.get_alert_by_id(alert_id)
        if not alert:
            abort(404, message="Alert not found")
        return alert

    @blp.route("/update", methods=["PUT"])
    @limiter.limit("60 per minute")
    @blp.arguments(UpdateAlertSchema, location="query")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin", "operator"])
    def update_alert(data):
        """Update alert status and severity (Admin & Operator)"""
        user = request.user
        success = alert_service.update_alert(
            alert_id=data["alert_id"],
            alert_severity=AlertSeverity(data["alert_severity"]),
            alert_status=AlertStatus(data["alert_status"]),
        )
        operational_service.log(
            user_id=user["uid"],
            email=user.get("email", ""),
            message=f"Updated alert {data['alert_id']} → {data['alert_status']}",
        )
        return {"success": success}

    @blp.route("/rules/create", methods=["POST"])
    @limiter.limit("60 per minute")
    @blp.arguments(CreateAlertRuleSchema, location="query")
    @blp.response(200, AlertRuleSchema)
    @auth_required(["admin"])
    def create_alert_rule(data):
        """Create a new alert rule (Admin only)"""
        user = request.user
        location = Coordinate(
            longitude=data["location"]["longitude"],
            latitude=data["location"]["latitude"],
        )
        rule = alert_service.create_alert_rule(
            author_id=user["uid"],
            name=data["name"],
            threshold=data["threshold"],
            location=location,
            radius=data["radius"],
            operator=ComparisonOperator(data["operator"]),
            sensor_type=SensorType(data["sensor_type"]),
        )
        operational_service.log(
            user_id=user["uid"],
            email=user.get("email", ""),
            message=f"Created alert rule '{rule.name}' (id: {rule.rule_id})",
        )
        return rule

    @blp.route("/rules/delete/<rule_id>", methods=["DELETE"])
    @limiter.limit("60 per minute")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin"])
    def delete_alert_rule(rule_id):
        """Delete an alert rule (Admin only)"""
        user = request.user
        success = alert_service.delete_alert_rule(rule_id)
        operational_service.log(
            user_id=user["uid"],
            email=user.get("email", ""),
            message=f"Deleted alert rule {rule_id}",
        )
        return {"success": success}

    @blp.route("/rules")
    @limiter.limit("60 per minute")
    @blp.response(200, AlertRuleSchema(many=True))
    @auth_required(["admin"])
    def get_all_alert_rules():
        """Get all alert rules (Admin only)"""
        return alert_service.get_all_alert_rules()

    @blp.route("/rules/<rule_id>")
    @limiter.limit("60 per minute")
    @blp.response(200, AlertRuleSchema)
    @auth_required(["admin"])
    def get_alert_rule(rule_id):
        """Get alert rule by ID (Admin only)"""
        rule = alert_service.get_alert_rule_by_id(rule_id)
        if not rule:
            abort(404, message="Alert rule not found")
        return rule

    @blp.route("/subscribe/<rule_id>", methods=["POST"])
    @limiter.limit("60 per minute")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin", "operator", "public"])
    def subscribe_to_alert(rule_id):
        """Subscribe to an alert rule"""
        user_id = request.user["uid"]
        success = alert_service.subscribe_to_alert(rule_id, user_id)
        return {"success": success}

    @blp.route("/unsubscribe/<rule_id>", methods=["DELETE"])
    @limiter.limit("60 per minute")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin", "operator", "public"])
    def unsubscribe_from_alert(rule_id):
        """Unsubscribe from an alert rule"""
        user_id = request.user["uid"]
        success = alert_service.unsubscribe_from_alert(rule_id, user_id)
        return {"success": success}

    @blp.route("/subscriptions", methods=["GET"])
    @limiter.limit("60 per minute")
    @blp.response(200, SubscriptionSchema(many=True))
    @auth_required(["admin", "operator", "public"])
    def get_my_subscriptions():
        """Get subscriptions for the authenticated user"""
        user_id = request.user["uid"]
        return alert_service.get_subscriptions_for_user(user_id)

    return blp