from dataclasses import dataclass
from enum import Enum

@dataclass
class Newsletter:
    newsletter_id: int
    profile_id: int
    generated_at: str
    content: str
    delivery_status: DeliveryStatus

class DeliveryStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"