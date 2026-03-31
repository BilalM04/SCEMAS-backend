from dataclasses import asdict
from typing import List

from models.AlertInformation import AlertInformation
from models.AlertSeverity import AlertSeverity
from models.AlertStatus import AlertStatus

class AlertDataProvider:
    def __init__(self, db):
        self.db = db
        self.collection = db.collection("alerts")

    def get_all_alerts(self) -> List[AlertInformation]:
        docs = self.collection.stream()
        return [self._from_doc(doc) for doc in docs]

    def save_alert(self, alert: AlertInformation) -> str:
        data = self._to_dict(alert)

        doc_ref = self.collection.add(data)
        return doc_ref[1].id

    def update_alert(self, alert_id: str, updates: dict) -> None:
        """
        updates example:
        {
            "status": AlertStatus.RESOLVED,
            "severity": AlertSeverity.HIGH
        }
        """

        if "severity" in updates and isinstance(updates["severity"], AlertSeverity):
            updates["severity"] = updates["severity"].value

        if "status" in updates and isinstance(updates["status"], AlertStatus):
            updates["status"] = updates["status"].value

        self.collection.document(alert_id).update(updates)

    def _to_dict(self, alert: AlertInformation) -> dict:
        data = asdict(alert)

        if isinstance(alert.severity, AlertSeverity):
            data["severity"] = alert.severity.value

        if isinstance(alert.status, AlertStatus):
            data["status"] = alert.status.value

        data.pop("alert_id", None)

        return data

    def _from_doc(self, doc) -> AlertInformation:
        data = doc.to_dict()

        return AlertInformation(
            alert_id=doc.id,
            rule_id=data.get("rule_id"),
            time=data.get("time"),
            severity=AlertSeverity(data.get("severity")),
            status=AlertStatus(data.get("status"))
        )