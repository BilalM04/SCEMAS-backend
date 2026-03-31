from dataclasses import dataclass

from models import AlertSeverity, AlertStatus

@dataclass
class AlertInformation:
    alert_id: str
    rule_id: str
    time: int
    severity: AlertSeverity
    status: AlertStatus