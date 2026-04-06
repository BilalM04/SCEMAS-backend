from marshmallow import Schema, fields
from marshmallow.validate import OneOf

from models.AccountRole import AccountRole
from models.AlertSeverity import AlertSeverity
from models.AlertStatus import AlertStatus
from models.ComparisonOperator import ComparisonOperator
from models.SensorType import SensorType

def enum_values(enum_cls):
    return [e.value for e in enum_cls]

class AccountSchema(Schema):
    user_id = fields.Str(required=True, metadata={"description": "Unique user ID"})
    email = fields.Email(required=True, metadata={"description": "User email address"})
    role = fields.Str(
        required=True,
        validate=OneOf(enum_values(AccountRole)),
        metadata={"description": "User role"}
    )


class LogSchema(Schema):
    log_id = fields.Str(required=True, metadata={"description": "ID of log data"})
    user_id = fields.Str(required=True, metadata={"description": "ID of the user who triggered the operation"})
    email = fields.Str(required=True, metadata={"description": "Email of the user who triggered the operation"})
    log_message = fields.Str(required=True, metadata={"description": "Log message"})
    time = fields.Int(required=True, metadata={"description": "Timestamp of the operation (epoch time)"})


class SystemHealthSchema(Schema):
    up_time = fields.Float(required=True, metadata={"description": "System uptime in seconds"})
    memory_usage = fields.Float(required=True, metadata={"description": "Memory usage percentage"})
    disk_space = fields.Float(required=True, metadata={"description": "Available disk space percentage"})
    cpu_usage = fields.Float(required=True, metadata={"description": "CPU usage percentage"})


class CoordinateSchema(Schema):
    longitude = fields.Float(required=True, metadata={"description": "Longitude"})
    latitude = fields.Float(required=True, metadata={"description": "Latitude"})


class AlertSchema(Schema):
    alert_id = fields.Str(
        required=True,
        metadata={"description": "Alert ID"}
    )
    rule_id = fields.Str(
        required=True,
        metadata={"description": "Rule ID"}
    )
    sensor_id = fields.Str(
        required=True,
        metadata={"description": "Sensor ID"}
    )
    rule_name = fields.Str(
        required=True,
        metadata={"description": "Rule name"}
    )
    time = fields.Int(
        required=True,
        metadata={"description": "Timestamp"}
    )
    severity = fields.Str(
        required=True,
        validate=OneOf(enum_values(AlertSeverity)),
        metadata={"description": "Alert severity"}
    )
    status = fields.Str(
        required=True,
        validate=OneOf(enum_values(AlertStatus)),
        metadata={"description": "Alert status"}
    )


class UpdateAlertSchema(Schema):
    alert_id = fields.Str(required=True, metadata={"description": "Alert ID"})
    alert_status = fields.Str(
        required=True,
        validate=OneOf(enum_values(AlertStatus)),
        metadata={"description": "New alert status"}
    )
    alert_severity = fields.Str(
        required=True,
        validate=OneOf(enum_values(AlertSeverity)),
        metadata={"description": "New alert severity"}
    )


class AlertRuleSchema(Schema):
    rule_id = fields.Str(required=True, metadata={"description": "Rule ID"})
    author_id = fields.Str(required=True, metadata={"description": "User who created the rule"})
    name = fields.Str(required=True)
    threshold = fields.Float(required=True)
    operator = fields.Str(
        required=True,
        validate=OneOf(enum_values(ComparisonOperator)),
        metadata={
            "description": "Comparison operator",
            "enum": enum_values(ComparisonOperator)
        }
    )
    location = fields.Nested(CoordinateSchema, required=True)
    radius = fields.Float(required=True)
    sensor_type = fields.Str(
        required=True,
        validate=OneOf(enum_values(SensorType)),
        metadata={
            "description": "Sensor type",
            "enum": enum_values(SensorType)
        }
    )
    created_at = fields.Int(
        required=True,
        metadata={"description": "Creation timestamp (epoch)"}
    )
    updated_at = fields.Int(
        required=True,
        metadata={"description": "Last update timestamp (epoch)"}
    )


class CreateAlertRuleSchema(Schema):
    name = fields.Str(required=True)
    threshold = fields.Float(required=True)
    operator = fields.Str(
        required=True,
        validate=OneOf(enum_values(ComparisonOperator))
    )
    location = fields.Nested(CoordinateSchema, required=True)
    radius = fields.Float(required=True)
    sensor_type = fields.Str(
        required=True,
        validate=OneOf(enum_values(SensorType))
    )


class SuccessResponseSchema(Schema):
    success = fields.Bool(required=True)


class SensorDataSchema(Schema):
    sensor_id = fields.Str(required=False)
    measurement = fields.Float(required=True)
    unit = fields.Str(required=True)

    time = fields.Int(
        required=True,
        metadata={"description": "Timestamp (epoch)"}
    )

    location = fields.Nested(CoordinateSchema, required=True)

    sensor_type = fields.Str(
        required=True,
        validate=OneOf(enum_values(SensorType)),
        metadata={
            "description": "Type of sensor",
            "enum": enum_values(SensorType)
        }
    )

    country = fields.Str(
        required=True,
        metadata={"description": "Country"}
    )

    city = fields.Str(
        required=True,
        metadata={"description": "City"}
    )


class AggregatedDataSchema(Schema):
    mean = fields.Float(required=True)
    median = fields.Float(required=True)
    mode = fields.Float(required=True)


class AggregatedResponseSchema(Schema):
    data = fields.Dict(
        keys=fields.Str(validate=OneOf(enum_values(SensorType))),
        values=fields.Nested(AggregatedDataSchema),
        metadata={"description": "Aggregated data per sensor type"}
    )


class SensorFilterSchema(Schema):
    country = fields.Str(required=False)
    city = fields.Str(required=False)

    sensor_type = fields.Str(
        required=False,
        validate=OneOf(enum_values(SensorType))
    )

    start_time = fields.Int(required=False, metadata={"description": "Start timestamp"})
    end_time = fields.Int(required=False, metadata={"description": "End timestamp"})


class ChangeRoleSchema(Schema):
    user_id = fields.Str(
        required=True,
        metadata={"description": "User ID"}
    )

    role = fields.Str(
        required=True,
        validate=OneOf(enum_values(AccountRole)),
        metadata={
            "description": "User role",
            "enum": enum_values(AccountRole)
        }
    )


class SubscriptionSchema(Schema):
    subscription_id = fields.Str(
        required=True,
        metadata={"description": "Subscription ID"}
    )
    subscriber_id = fields.Str(
        required=True,
        metadata={"description": "Subscriber (user) ID"}
    )
    rule_id = fields.Str(
        required=True,
        metadata={"description": "Rule ID"}
    )
    rule_name = fields.Str(
        required=True,
        metadata={"description": "Rule name"}
    )