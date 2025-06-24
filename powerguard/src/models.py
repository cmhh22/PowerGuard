from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List

@dataclass
class Outage:
    id: int
    zone: str
    start_time: datetime
    duration_estimated: Optional[int] = None  # duration in minutes
    resolved: bool = False
    resolved_time: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": self.id,
            "zone": self.zone,
            "start_time": self.start_time.isoformat(),
            "duration_estimated": self.duration_estimated,
            "resolved": self.resolved,
            "resolved_time": self.resolved_time.isoformat() if self.resolved_time else None
        }

    @staticmethod
    def from_dict(data):
        return Outage(
            id=data["id"],
            zone=data["zone"],
            start_time=datetime.fromisoformat(data["start_time"]),
            duration_estimated=data.get("duration_estimated"),
            resolved=data.get("resolved", False),
            resolved_time=datetime.fromisoformat(data["resolved_time"]) if data.get("resolved_time") else None
        )

@dataclass
class User:
    id: int
    name: str
    contact: str  # email or phone
    subscriptions: List[int] = field(default_factory=list)
