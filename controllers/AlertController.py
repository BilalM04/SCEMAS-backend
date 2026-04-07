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
    blp = Blueprint("alerts", "alerts", url_prefix="/alerts", description="Alert endpoints")

    # -------------------------
    # Helpers
    # -------------------------
    def safe_enum(enum_class, value, field_name):
        try:
            return enum_class(value)
        except Exception:
            abort(400, message=f"Invalid value for {field_name}: {value}")

    def handle_exception(e, message="Internal server error"):
        print(f"[ERROR] {message}: {str(e)}")
        abort(500, message=message)

    # -------------------------
    # Alerts
    # -------------------------
    @blp.route("/")
    @limiter.limit("60 per minute")
    @blp.response(200, AlertSchema(many=True))
    @auth_required(["admin", "operator"])
    def get_alerts():
        """Get all alerts (Admin & Operator)"""
        try:
            alerts = alert_service.get_all_alerts()
            return [alert.to_dict() for alert in alerts]
        except Exception as e:
            handle_exception(e, "Failed to fetch alerts")

    @blp.route("/<alert_id>")
    @limiter.limit("60 per minute")
    @blp.response(200, AlertSchema)
    @auth_required(["admin", "operator"])
    def get_alert(alert_id: str):
        """Get alert by ID (Admin & Operator)"""
        try:
            alert = alert_service.get_alert_by_id(alert_id)
            if not alert:
                abort(404, message="Alert not found")
            return alert.to_dict()
        except Exception as e:
            handle_exception(e, "Failed to fetch alert")

    @blp.route("/update", methods=["PUT"])
    @limiter.limit("60 per minute")
    @blp.arguments(UpdateAlertSchema, location="query")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin", "operator"])
    def update_alert(data):
        """Update alert status and severity (Admin & Operator)"""
        user = request.user

        try:
            severity = safe_enum(AlertSeverity, data["alert_severity"], "alert_severity")
            status = safe_enum(AlertStatus, data["alert_status"], "alert_status")

            success = alert_service.update_alert(
                alert_id=data["alert_id"],
                alert_severity=severity,
                alert_status=status,
            )

            if not success:
                abort(404, message="Alert not found or update failed")

            operational_service.log_event(
                user_id=user["uid"],
                email=user.get("email", ""),
                message=f"Updated alert {data['alert_id']} → {data['alert_status']}",
            )

            return {"success": True}

        except Exception as e:
            handle_exception(e, "Failed to update alert")

    # -------------------------
    # Alert Rules
    # -------------------------
    @blp.route("/rules/create", methods=["POST"])
    @limiter.limit("60 per minute")
    @blp.arguments(CreateAlertRuleSchema, location="query")
    @blp.response(200, AlertRuleSchema)
    @auth_required(["admin"])
    def create_alert_rule(data):
        """Create a new alert rule (Admin only)"""
        user = request.user

        try:
            location = Coordinate(
                longitude=data["longitude"],
                latitude=data["latitude"],
            )

            operator = safe_enum(ComparisonOperator, data["operator"], "operator")
            sensor_type = safe_enum(SensorType, data["sensor_type"], "sensor_type")

            rule = alert_service.create_alert_rule(
                author_id=user["uid"],
                name=data["name"],
                threshold=data["threshold"],
                location=location,
                radius=data["radius"],
                operator=operator,
                sensor_type=sensor_type,
            )

            operational_service.log_event(
                user_id=user["uid"],
                email=user.get("email", ""),
                message=f"Created alert rule '{rule.name}' (id: {rule.rule_id})",
            )

            return rule.to_dict()

        except Exception as e:
            handle_exception(e, "Failed to create alert rule")

    @blp.route("/rules/delete/<rule_id>", methods=["DELETE"])
    @limiter.limit("60 per minute")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin"])
    def delete_alert_rule(rule_id):
        """Delete an alert rule (Admin Only)"""
        user = request.user

        try:
            success = alert_service.delete_alert_rule(rule_id)

            if not success:
                abort(404, message="Alert rule not found")

            operational_service.log_event(
                user_id=user["uid"],
                email=user.get("email", ""),
                message=f"Deleted alert rule {rule_id}",
            )

            return {"success": True}

        except Exception as e:
            handle_exception(e, "Failed to delete alert rule")

    @blp.route("/rules")
    @limiter.limit("60 per minute")
    @blp.response(200, AlertRuleSchema(many=True))
    @auth_required(["admin", "operator", "public"])
    def get_all_alert_rules():
        """Get all alert rules (Admin, Operator, & Public)"""
        try:
            rules = alert_service.get_all_alert_rules()
            return [rule.to_dict() for rule in rules]
        except Exception as e:
            handle_exception(e, "Failed to fetch alert rules")

    @blp.route("/rules/<rule_id>")
    @limiter.limit("60 per minute")
    @blp.response(200, AlertRuleSchema)
    @auth_required(["admin", "operator", "public"])
    def get_alert_rule(rule_id):
        """Get alert rule by ID (Admin, Operator, & Public)"""
        try:
            rule = alert_service.get_alert_rule_by_id(rule_id)
            if not rule:
                abort(404, message="Alert rule not found")
            return rule.to_dict()
        except Exception as e:
            handle_exception(e, "Failed to fetch alert rule")

    # -------------------------
    # Subscriptions
    # -------------------------
    @blp.route("/subscribe/<rule_id>", methods=["POST"])
    @limiter.limit("60 per minute")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin", "operator", "public"])
    def subscribe_to_alert(rule_id):
        """Subscribe to an alert rule"""
        user_id = request.user["uid"]

        try:
            success = alert_service.subscribe_to_alert(rule_id, user_id)

            if not success:
                abort(404, message="Rule not found or already subscribed")

            return {"success": True}

        except Exception as e:
            handle_exception(e, "Failed to subscribe to alert")

    @blp.route("/unsubscribe/<rule_id>", methods=["DELETE"])
    @limiter.limit("60 per minute")
    @blp.response(200, SuccessResponseSchema)
    @auth_required(["admin", "operator", "public"])
    def unsubscribe_from_alert(rule_id):
        """Unsubscribe from an alert rule"""
        user_id = request.user["uid"]

        try:
            success = alert_service.unsubscribe_from_alert(user_id, rule_id)

            if not success:
                abort(404, message="Subscription not found")

            return {"success": True}

        except Exception as e:
            handle_exception(e, "Failed to unsubscribe from alert")

    @blp.route("/subscriptions", methods=["GET"])
    @limiter.limit("60 per minute")
    @blp.response(200, SubscriptionSchema(many=True))
    @auth_required(["admin", "operator", "public"])
    def get_my_subscriptions():
        """Get subscriptions for the authenticated user"""
        user_id = request.user["uid"]

        try:
            return alert_service.get_subscriptions_for_user(user_id)
        except Exception as e:
            handle_exception(e, "Failed to fetch subscriptions")

    return blp