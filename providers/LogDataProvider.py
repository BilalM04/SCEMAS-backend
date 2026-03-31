from dataclasses import asdict
from typing import List

from models.LogInformation import LogInformation

class LogDataProvider:
    def __init__(self, db):
        self.db = db
        self.collection = db.collection("logs")

    def get_all_logs(self) -> List[LogInformation]:
        docs = self.collection.stream()

        logs = []
        for doc in docs:
            data = doc.to_dict()

            log = LogInformation(
                log_id=doc.id,
                user_id=data.get("user_id"),
                log_message=data.get("log_message"),
                time=data.get("time")
            )
            logs.append(log)

        return logs

    def save_log(self, log: LogInformation) -> str:
        data = asdict(log)

        data.pop("log_id", None)

        doc_ref = self.collection.add(data)
        return doc_ref[1].id