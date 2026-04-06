from dataclasses import dataclass

@dataclass
class AggregatedData:
    mean: float
    median: float
    mode: float

    def to_dict(self) -> dict:
        return {
            "mean": self.mean,
            "median": self.median,
            "mode": self.mode,
        }