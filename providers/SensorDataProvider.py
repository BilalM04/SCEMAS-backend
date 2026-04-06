from dataclasses import asdict
from typing import List, Optional
from datetime import datetime

from models.SensorData import SensorData
from models.Coordinate import Coordinate
from models.SensorType import SensorType

class SensorDataProvider:
    def __init__(self, db):
        self.db = db
        self.collection = db.collection("sensors")

    def get_all_sensor_data(self) -> List[SensorData]:
        docs = self.collection.stream()
        return [s for doc in docs if (s := self._from_doc(doc)) is not None]
    
    def get_sensor_data_by_id(self, sensor_id: str) -> SensorData | None:
        doc = self.collection.document(sensor_id).get()
        return self._from_doc(doc)
    
    def query_sensor_data(
        self,
        sensor_type: SensorType,
        city: Optional[str] = None,
        country: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[SensorData]:
        query = self.collection
        print(f"Querying sensor data with filters - sensor_type: {sensor_type.value}, city: {city}, country: {country}, start_time: {start_time}, end_time: {end_time}")
        if sensor_type:
            query = query.where("sensor_type", "==", sensor_type.value)

        results = [
            s for doc in query.stream()
            if (s := self._from_doc(doc)) is not None
        ]

        if not results:
            return results

        if city:
            city_lower = city.lower()
            results = [
                r for r in results
                if r.city and r.city.lower() == city_lower
            ]

        if country:
            country_lower = country.lower()
            results = [
                r for r in results
                if r.country and r.country.lower() == country_lower
            ]

        if start_time is not None:
            results = [r for r in results if r.time >= start_time]

        if end_time is not None:
            results = [r for r in results if r.time <= end_time]
        
        return results

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

        if data is None:
            return None

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
