# =============================================================================
# models.py — Domain models for the NoQ queue system.
#
# Contains:
#   - ServiceType: enum of available service categories (passport, tax, etc.)
#   - Customer: identifies a person in the queue (user_id + name)
#   - Ticket: the central entity — links a Customer to a ServiceType, tracks
#     priority, status (WAITING/SERVED/CANCELLED), and timing.
#
# Design notes:
#   - Ticket.priority_level: 0 = normal (goes into FIFO deque),
#     >0 = priority (goes into a max-heap in QueueManager).
#   - Ticket.__lt__ exists for natural sorting by issue time, but the heap
#     in queues.py sorts by (-priority, counter) tuples instead.
# =============================================================================

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
