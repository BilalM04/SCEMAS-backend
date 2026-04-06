from statistics import multimode
from typing import Optional
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
        sensor_type: SensorType,
        city: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> dict[SensorType, AggregatedData]:
        # listToAggregate = self.sensor_provider.get_all_sensor_data()
        # results: dict[SensorType, AggregatedData] = {}
        # sensor_type_data = [s for s in listToAggregate
        #     if (s.sensor_type == sensor_type)
        #     and (city is None or s.city == city)
        #     and (start_time is None or s.time >= start_time)
        #     and (end_time is None or s.time <= end_time)
        # ]

        query_sensor_data = self.sensor_provider.query_sensor_data(
            sensor_type=sensor_type,
            city=city,
            start_time=start_time,
            end_time=end_time
        )
        print(f"Queried {len(query_sensor_data)} records for sensor type {sensor_type}, city {city}, start_time {start_time}, end_time {end_time}")
        if not sensor_type_data:
            return results
        measurements = [s.measurement for s in query_sensor_data]
        mean = sum(measurements) / len(measurements)
        median = sorted(measurements)[len(measurements) // 2]
        mode = multimode(measurements)

        ad = AggregatedData(
            mean=mean,
            median=median,
            mode=mode
        )
        results[sensor_type] = ad
        return results

    def get_all_sensor_data(self) -> list[SensorData]:
        return self.sensor_provider.get_all_sensor_data()
    
    #temporary
    def delete_sensor_data(self, sensor_id: str):
        return self.sensor_provider.delete_sensor_data(sensor_id)

    def save_sensor_data(
        self,
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
                sensor_id="",
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