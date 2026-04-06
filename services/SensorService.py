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
        filter_sensor_type: Optional[SensorType] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> dict[SensorType, AggregatedData]:

        sensors_to_aggregate = []
        if filter_sensor_type:
            sensors_to_aggregate.append(filter_sensor_type)
        elif (len(sensors_to_aggregate) == 0):
            sensors_to_aggregate = list(SensorType)

        print(f"Sensors to aggregate: {[s.value for s in sensors_to_aggregate]}")

        results = {}
        for sensor_type in sensors_to_aggregate:

            query_sensor_data = self.sensor_provider.query_sensor_data(
                sensor_type=sensor_type,
                city=city,
                country=country,
                start_time=start_time,
                end_time=end_time
            )

            if (len(query_sensor_data) == 0):
                print(f"No data found for sensor type {sensor_type}, city {city}, country {country}, start_time {start_time}, end_time {end_time}")
                continue
            # print(f"Queried {len(query_sensor_data)} records for sensor type {sensor_type}, city {city}, start_time {start_time}, end_time {end_time}")
        # if not sensor_type_data:
        #     return results
            measurements = [s.measurement for s in query_sensor_data]
            
            mean = 0
            median = 0
            mode = 0
            if len(measurements) != 0:
                mean = sum(measurements) / len(measurements)
                median = sorted(measurements)[len(measurements) // 2]
                mode = multimode(measurements)[0]

            ad = {
                "mean": mean,
                "median": median,
                "mode": mode
            }
            # print(ad)
            results[sensor_type] = ad
            # print(results)
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