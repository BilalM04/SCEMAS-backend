# services/SensorService.py
class SensorService:
    def __init__(self, sensor_provider: SensorDataProvider, alert_service=None):
        self.sensor_provider = sensor_provider
        self.alert_service = alert_service   # injected; None = no alerting

    def save_sensor_data(
        self,
        measurement: float,
        unit: str,
        time: int,
        location: Coordinate,
        sensor_type: SensorType,
        country: str,
        city: str,
    ) -> bool:
        from models.SensorData import SensorData
        sensor = SensorData(
            sensor_id="",
            measurement=measurement,
            unit=unit,
            time=time,
            location=location,
            sensor_type=sensor_type,
            country=country,
            city=city,
        )
        sensor_id = self.sensor_provider.save_sensor_data(sensor)

        # Trigger alert evaluation (sequence diagram: Ingest sensor data)
        if self.alert_service:
            self.alert_service.evaluate_sensor_data(
                sensor_id=sensor_id,
                sensor_type=sensor_type,
                measurement=measurement,
                location=location,
                timestamp=time,
                country=country,
                city=city,
            )
        return True