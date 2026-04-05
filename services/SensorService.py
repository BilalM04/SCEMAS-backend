from models.AggregatedData import AggregatedData
from models.Coordinate import Coordinate
from models.SensorData import SensorData
from models.SensorType import SensorType

from providers.SensorDataProvider import SensorDataProvider


class SensorService:
    def __init__(self, sensor_provider: SensorDataProvider):
        self.sensor_provider = sensor_provider

    def get_aggregated_data(
        self,
        location: Coordinate,
        radius: float,
        start_time: int,
        end_time: int,
    ) -> dict[SensorType, AggregatedData]:
        pass

    def get_all_sensor_data(self) -> list[SensorData]:
        return self.sensor_provider.get_all_sensor_data()

    def save_sensor_data(
        self,
        sensor_id: str,
        measurement: float,
        unit: str,
        time: int,
        location: Coordinate,
        sensor_type: SensorType,
        country: str,
        city: str
    )-> bool:
        try:
            sensor = SensorData(
                sensor_id=sensor_id,
                measurement=measurement,
                unit=unit,
                time=time,
                location=location,
                sensor_type=sensor_type,
                country=country,
                city=city
            )
            self.sensor_provider.save_sensor_data(sensor)
            return True
        except Exception as e:
            print(f"Error occurred while saving sensor data: {e}")
            return False