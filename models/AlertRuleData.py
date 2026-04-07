from dataclasses import dataclass
from models import ComparisonOperator, Coordinate, SensorType

@dataclass
class AlertRuleData:
    rule_id: str
    author_id: str
    name: str
    threshold: float
    operator: ComparisonOperator
    location: Coordinate
    radius: float
    sensor_type: SensorType
    created_at: int
    updated_at: int

    def evaluate(self, value: float) -> bool:
        if self.operator == ComparisonOperator.GREATER_THAN:
            return value > self.threshold
        elif self.operator == ComparisonOperator.LESS_THAN:
            return value < self.threshold
        elif self.operator == ComparisonOperator.GREATER_OR_EQUAL:
            return value >= self.threshold
        elif self.operator == ComparisonOperator.LESS_OR_EQUAL:
            return value <= self.threshold
        elif self.operator == ComparisonOperator.EQUAL:
            return value == self.threshold
        elif self.operator == ComparisonOperator.NOT_EQUAL:
            return value != self.threshold
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")
        
    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "author_id": self.author_id,
            "name": self.name,
            "threshold": self.threshold,
            "operator": self.operator.value,
            "location": {
                "longitude": self.location.longitude,
                "latitude": self.location.latitude,
            },
            "radius": self.radius,
            "sensor_type": self.sensor_type.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }