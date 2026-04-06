from models.SystemHealth import SystemHealth
from models.LogInformation import LogInformation
from providers.LogDataProvider import LogDataProvider
import psutil
import datetime

class OperationalService:
    def __init__(self, log_provider: LogDataProvider):
        self.log_provider = log_provider

    def log_event(self, user_id: str, message: str, email: str) -> bool:
        log = LogInformation(#create LogInfo
            log_id="",
            user_id=user_id,
            log_message=message,
            time=int(datetime.datetime.now().timestamp()),
            email=email
        )
        try:#save log to DB
            id=self.log_provider.save_log(log)
            if id:#check for successful save
                return True
            return False
        except Exception:
            return False

    def get_system_health(self) -> SystemHealth:
        #retrieve data
        up_time = int((datetime.datetime.now()-datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds())
        memory_usage = psutil.virtual_memory().percent
        disk_space = psutil.disk_usage('/').percent
        cpu_usage = psutil.cpu_percent(interval=1)
        health = SystemHealth(#create health object
            up_time=up_time,
            memory_usage=memory_usage,
            disk_space=disk_space,
            cpu_usage=cpu_usage
        )

        return health

    def get_all_logs(self) -> list[LogInformation]:
        return self.log_provider.get_all_logs()

