from dataclasses import asdict
from typing import List

from models.AlertRuleData import AlertRuleData
from models.ComparisonOperator import ComparisonOperator
from models.SensorType import SensorType
from models.Coordinate import Coordinate

class AlertRuleDataProvider:
    def __init__(self, db):
        self.db = db
        self.collection = db.collection("alertrules")

    def get_all_alert_rules(self) -> List[AlertRuleData]:
        docs = self.collection.stream()
        return [self._from_doc(doc) for doc in docs]

    def save_alert_rule(self, rule: AlertRuleData) -> str:
        data = self._to_dict(rule)

        doc_ref = self.collection.add(data)
        return doc_ref[1].id

    def update_alert_rule(self, rule_id: str, updates: dict) -> None:
        """
        Example updates:
        {
            "threshold": 50,
            "operator": ComparisonOperator.GREATER_THAN,
            "location": Coordinate(...),
            "sensor_type": SensorType.TEMPERATURE
        }
        """

        if "operator" in updates and isinstance(updates["operator"], ComparisonOperator):
            updates["operator"] = updates["operator"].value

        if "sensor_type" in updates and isinstance(updates["sensor_type"], SensorType):
            updates["sensor_type"] = updates["sensor_type"].value

        if "location" in updates and isinstance(updates["location"], Coordinate):
            updates["location"] = asdict(updates["location"])

        self.collection.document(rule_id).update(updates)

    def delete_alert_rule(self, rule_id: str) -> None:
        self.collection.document(rule_id).delete()

    def _to_dict(self, rule: AlertRuleData) -> dict:
        data = asdict(rule)

        data["location"] = asdict(rule.location)

        if isinstance(rule.operator, ComparisonOperator):
            data["operator"] = rule.operator.value

        if isinstance(rule.sensor_type, SensorType):
            data["sensor_type"] = rule.sensor_type.value

        data.pop("rule_id", None)

        return data

    def _from_doc(self, doc) -> AlertRuleData:
        data = doc.to_dict()

        return AlertRuleData(
            rule_id=doc.id,
            author_id=data.get("author_id"),
            name=data.get("name"),
            threshold=data.get("threshold"),
            operator=ComparisonOperator(data.get("operator")),
            location=Coordinate(**data.get("location")),
            radius=data.get("radius"),
            sensor_type=SensorType(data.get("sensor_type")),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )