from models.AlertInformation import AlertInformation
from models.AlertRuleData import AlertRuleData
from models.AlertSeverity import AlertSeverity
from models.AlertStatus import AlertStatus
from models.ComparisonOperator import ComparisonOperator
from models.Coordinate import Coordinate
from models.SensorType import SensorType
from models.Subscription import Subscription

from providers.AlertDataProvider import AlertDataProvider
from providers.AlertRuleDataProvider import AlertRuleDataProvider
from providers.SubscriptionDataProvider import SubscriptionDataProvider


class AlertService:
    def __init__(
        self,
        rule_provider: AlertRuleDataProvider,
        alert_provider: AlertDataProvider,
        subscription_provider: SubscriptionDataProvider,
    ):
        self.rule_provider = rule_provider
        self.alert_provider = alert_provider
        self.subscription_provider = subscription_provider

    def create_alert_rule(
        self,
        author_id: str,
        threshold: float,
        location: Coordinate,
        radius: float,
        operator: ComparisonOperator,
        sensor_type: SensorType,
    ) -> AlertRuleData:
        now = int(time.time())
        rule = AlertRuleData(
            rule_id = "",
            author_id="",
            name=name,
            threshold = threshold,
            operator = operator, 
            location = location, 
            radius = radius, 
            sensor_type = sensor_type,
            created_at = now, 
            updated_at = now,
        )
        rule_id = self.rule_provider.save_alert_rule(rule)
        rule.rule_id = rule_id
        return rule

    def delete_alert_rule(self, rule_id: str) -> bool:
        self.rule_provider.delete_alert_rule(rule_id)
        return True
    def get_all_alert_rules(self) -> list[AlertRuleData]:
        return self.rule_provider.get_all_alert_rules()

    def get_all_alerts(self) -> list[AlertInformation]:
        return self.rule_provider.get_all_alert_rules()

    def get_alert_rule_by_id(self, rule_id: str) -> AlertRuleData:
        return self.rule_provider.get_rule_by_id(rule_id)

    def update_alert(
        self,
        alert_id: str,
        alert_severity: AlertSeverity,
        alert_status: AlertStatus,
    ) -> bool:
        self.alert_provider.update_alert(alert_id, {
            "severity": alert_severity, 
            "status": alert_status,
        })
        return True

    def subscribe_to_alert(self, rule_id: str, user_id: str) -> bool:
        rule = self.rule_provider.get_rule_by_id(rule_id)
        sub = Subscription(
            subscription_id="",
            subscriber_id=user_id,
            rule_id=rule_id,
            rule_name=rule.name,
        )
        self.subscription_provider.save_subscription(sub)
        return True

    def unsubscribe_from_alert(self, subscription_id: str) -> bool:
        subs = self.subscription_provider.get_all_subscriptions()
        for sub in subs:
            if sub.subscriber_id == user_id and sub.rule_id == rule_id:
                self.subscription_provider.delete_subscription(sub.subscription_id)
                return True
        return False
    
    def get_subscriptions_for_user(self, user_id: str) -> list[Subscription]:
        all_subs = self.subscription_provider.get_all_subscriptions()
        return [s for s in all_subs if s.subscriber_id == user_id]
    
    def evaluate_sensor_data(
            self, 
            sensor_id: str, 
            sensor_type: SensorType, 
            measurement: float, 
            location: Coordinate, 
            timestamp: int, 
            country: str, 
            city: str, 
        ) -> None:

        rules = self.rule_provider.get_all_alert_rules()
        for rule in rules:
            if rule.sensor_type != sensor_type:
                continue
            if not self._within_radius(location, rule.location, rule.radius):
                continue
            if rule.evaluate(measurement):
                self._fire_alert(rule, sensor_id, timestamp, country, city)
    def _within_radius(
        self,
        sensor_loc: Coordinate,
        rule_loc: Coordinate,
        radius_km: float,
    ) -> bool:
        R = 6371.0
        lat1, lon1 = math.radians(sensor_loc.latitude), math.radians(sensor_loc.longitude)
        lat2, lon2 = math.radians(rule_loc.latitude), math.radians(rule_loc.longitude)
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return 2 * R * math.asin(math.sqrt(a)) <= radius_km

    def _fire_alert(
        self,
        rule: AlertRuleData,
        sensor_id: str,
        timestamp: int,
        country: str,
        city: str,
    ) -> None:
        alert = AlertInformation(
            alert_id="",
            rule_id=rule.rule_id,
            sensor_id=sensor_id,
            rule_name=rule.name,
            time=timestamp,
            sensor_type=rule.sensor_type,
            severity=AlertSeverity.LOW,      # default; operators can escalate
            status=AlertStatus.ACTIVE,
            country=country,
            city=city,
        )
        self.alert_provider.save_alert(alert)