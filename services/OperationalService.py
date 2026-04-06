from models.SystemHealth import SystemHealth
from models.LogInformation import LogInformation
from providers.LogDataProvider import LogDataProvider
import datetime

class OperationalService:
    def __init__(self, log_provider: LogDataProvider):
        self.log_provider = log_provider

    def log_event(self, user_id: str, message: str) -> bool: #Not sure how to get the user email from user id right now
        log = LogInformation(
            log_id="",
            user_id=user_id,
            log_message=message,
            time=int(datetime.datetime.now().timestamp()),
            email="..."
        )
        try:
            id=self.log_provider.save_log(log)
            if id:
                return True
            return False
        except Exception:
            return False

    def get_system_health(self) -> SystemHealth:
        pass 

    def get_all_logs(self) -> list[LogInformation]:
        return self.log_provider.get_all_logs()

