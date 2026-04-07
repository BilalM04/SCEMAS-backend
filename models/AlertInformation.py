from dataclasses import dataclass

from models import AlertSeverity, AlertStatus
from models.SensorType import SensorType

@dataclass
class AlertInformation:
    alert_id: str
    rule_id: str
    sensor_id: str
    rule_name: str
    time: int
    sensor_type: SensorType
    severity: AlertSeverity
    status: AlertStatus
    country: str
    city: str

    def to_dict(self) -> dict:
        return {
            "alert_id": self.alert_id,
            "rule_id": self.rule_id,
            "sensor_id": self.sensor_id,
            "rule_name": self.rule_name,
            "time": self.time,
            "sensor_type": self.sensor_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "country": self.country,
            "city": self.city,
        }