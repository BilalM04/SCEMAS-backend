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
        pass

    def save_sensor_data(
        self,
        measurement: float,
        unit: str,
        time: int,
        location: Coordinate,
        sensor_type: SensorType,
    ) -> bool:
        pass