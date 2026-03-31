from dataclasses import asdict
from typing import List

from models.Subscription import Subscription

class SubscriptionDataProvider:
    def __init__(self, db):
        self.db = db
        self.collection = db.collection("subscriptions")

    def get_all_subscriptions(self) -> List[Subscription]:
        docs = self.collection.stream()
        return [self._from_doc(doc) for doc in docs]

    def save_subscription(self, sub: Subscription) -> str:
        data = self._to_dict(sub)

        doc_ref = self.collection.add(data)
        return doc_ref[1].id

    def delete_subscription(self, subscription_id: str) -> None:
        self.collection.document(subscription_id).delete()

    def _to_dict(self, sub: Subscription) -> dict:
        data = asdict(sub)

        data.pop("subscription_id", None)

        return data

    def _from_doc(self, doc) -> Subscription:
        data = doc.to_dict()

        return Subscription(
            subscription_id=doc.id,
            subscriber_id=data.get("subscriber_id"),
            rule_id=data.get("rule_id")
        )