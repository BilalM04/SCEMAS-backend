from dataclasses import asdict
from typing import List

from models.SensorData import SensorData
from models.Coordinate import Coordinate
from models.SensorType import SensorType

class SensorDataProvider:
    def __init__(self, db):
        self.db = db
        self.collection = db.collection("sensors")

    def get_all_sensor_data(self) -> List[SensorData]:
        docs = self.collection.stream()
        return [self._from_doc(doc) for doc in docs]
    
    def get_sensor_data_by_id(self, sensor_id: str) -> SensorData:
        doc = self.collection.document(sensor_id).get()
        return self._from_doc(doc)

    def save_sensor_data(self, sensor: SensorData) -> str:
        data = self._to_dict(sensor)

        doc_ref = self.collection.add(data)
        return doc_ref[1].id

    def delete_sensor_data(self, sensor_id: str) -> None:
        self.collection.document(sensor_id).delete()

    def _to_dict(self, sensor: SensorData) -> dict:
        data = asdict(sensor)

        data["location"] = asdict(sensor.location)

        if isinstance(sensor.sensor_type, SensorType):
            data["sensor_type"] = sensor.sensor_type.value

        data.pop("sensor_id", None)

        return data

    def _from_doc(self, doc) -> SensorData:
        data = doc.to_dict()

        return SensorData(
            sensor_id=doc.id,
            measurement=data.get("measurement"),
            unit=data.get("unit"),
            time=data.get("time"),
            location=Coordinate(**data.get("location")),
            sensor_type=SensorType(data.get("sensor_type")),
            country=data.get("country"),
            city=data.get("city")
        )
