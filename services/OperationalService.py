from models.SystemHealth import SystemHealth
from models.LogInformation import LogInformation
from providers.LogDataProvider import LogDataProvider

class OperationalService:
    def __init__(self, log_provider: LogDataProvider):
        self.log_provider = log_provider

    def log_event(self, user_id: str, message: str) -> bool:
        pass 

    def get_system_health(self) -> SystemHealth:
        pass 

    def get_all_logs(self) -> list[LogInformation]:
        pass 

