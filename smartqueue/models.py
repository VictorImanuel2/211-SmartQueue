from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class ServiceType(str, Enum):
    PASSPORT = "passport"
    TAX = "tax"
    SUPPORT = "support"
    MUNICIPAL = "municipal"

@dataclass
class Customer:
    user_id: str
    name: str

@dataclass
class Ticket:
    ticket_id: str
    customer: Customer
    service: ServiceType
    office_id: str
    issued_at: datetime
    expected_minutes: int
    priority_level: int = 0 # 0 is normal, higher is more urgent
    status: str = "WAITING" # WAITING, SERVED, CANCELLED
    
    def __lt__(self, other):
        # This is needed for the heap if we were putting Ticket objects directly into heap, 
        # but we are putting tuples (-priority, counter, ticket_id).
        # Still useful for natural sorting if needed.
        return self.issued_at < other.issued_at
