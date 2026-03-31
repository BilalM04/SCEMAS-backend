from models.AlertInformation import AlertInformation
from models.AlertRuleData import AlertRuleData
from models.AlertSeverity import AlertSeverity
from models.AlertStatus import AlertStatus
from models.ComparisonOperator import ComparisonOperator
from models.Coordinate import Coordinate
from models.SensorType import SensorType

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
    ) -> bool:
        pass

    def delete_alert_rule(self, rule_id: str) -> bool:
        pass

    def get_all_alert_rules(self) -> list[AlertRuleData]:
        pass

    def get_all_alerts(self) -> list[AlertInformation]:
        pass

    def update_alert(
        self,
        alert_id: str,
        alert_severity: AlertSeverity,
        alert_status: AlertStatus,
    ) -> bool:
        pass

    def subscribe_to_alert(self, rule_id: str, user_id: str) -> bool:
        pass

    def unsubscribe_from_alert(self, subscription_id: str) -> bool:
        pass