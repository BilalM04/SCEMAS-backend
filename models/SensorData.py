from dataclasses import dataclass

from models import Coordinate, SensorType

@dataclass
class SensorData:
    sensor_id: str
    measurement: float
    unit: str
    time: int
    location: Coordinate
    sensor_type: SensorType
    country: str
    city: str

    def to_dict(self) -> dict:
        return {
            "sensor_id": self.sensor_id,
            "measurement": self.measurement,
            "unit": self.unit,
            "time": self.time,
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
            },
            "sensor_type": self.sensor_type.value,
            "country": self.country,
            "city": self.city,
        }