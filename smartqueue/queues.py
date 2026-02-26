import heapq
from collections import deque
from typing import Dict, List, Tuple, Optional
from .models import Ticket, Customer, ServiceType
from .utils import generate_id, get_current_time

class QueueManager:
    """
    Core backend logic for SmartQueue.
    Manages queues, priority heaps, and fast lookups.
    """

    def __init__(self):
        # O(1) Lookups
        # Map ticket_id -> Ticket object
        self.active_tickets_by_id: Dict[str, Ticket] = {}
        
        # Map (office_id, user_id, service) -> ticket_id. Ensures 1 active ticket per user/service.
        self.active_ticket_by_user: Dict[Tuple[str, str, str], str] = {}

        # O(1) FIFO Queues for normal customers (priority = 0)
        # Map (office_id, service) -> deque[ticket_id]
        self.normal_queues: Dict[Tuple[str, str], deque] = {}

        # O(log n) Priority Queues for priority customers (priority > 0)
        # Map (office_id, service) -> list[(-priority, counter, ticket_id)]
        self.priority_heaps: Dict[Tuple[str, str], List] = {}

        # Global counter for stable heap ordering
        self.counter = 0

        # Stats tracking for analytics
        self.served_count: Dict[str, int] = {}
        self.total_wait_time_sum: Dict[str, float] = {} # Sum of wait times in minutes

    def issue_ticket(self, user_id: str, name: str, service: str, 
                     priority_level: int = 0, expected_minutes: int = 10, 
                     office_id: str = "default") -> Ticket:
        """
        O(1) (Amortized) - Issues a new ticket.
        - Checks for existing ticket: O(1) dictionary lookup
        - Appends to deque: O(1) OR Pushes to heap: O(log k)
        """
        try:
            service_enum = ServiceType(service)
        except ValueError:
            raise ValueError(f"Invalid service type: {service}")

        # Enforce usage limits: 1 ticket per user per (office, service)
        user_key = (office_id, user_id, service_enum.value)
        if user_key in self.active_ticket_by_user:
            existing_id = self.active_ticket_by_user[user_key]
            raise ValueError(f"User {user_id} already has an active ticket: {existing_id}")

        # Create Ticket
        ticket_id = generate_id()
        customer = Customer(user_id=user_id, name=name)
        ticket = Ticket(
            ticket_id=ticket_id,
            customer=customer,
            service=service_enum,
            office_id=office_id,
            issued_at=get_current_time(),
            expected_minutes=expected_minutes,
            priority_level=priority_level,
            status="WAITING"
        )

        # Update O(1) Lookups
        self.active_tickets_by_id[ticket_id] = ticket
        self.active_ticket_by_user[user_key] = ticket_id

        # Add to Queue Structure
        queue_key = (office_id, service_enum.value)
        
        if priority_level > 0:
            # Priority Queue -> Heap
            # O(log n) push
            if queue_key not in self.priority_heaps:
                self.priority_heaps[queue_key] = []
            
            # Use negative priority for Max-Heap behavior simulation with Min-Heap
            self.counter += 1
            entry = (-priority_level, self.counter, ticket_id)
            heapq.heappush(self.priority_heaps[queue_key], entry)
        else:
            # Normal Queue -> Deque
            # O(1) append
            if queue_key not in self.normal_queues:
                self.normal_queues[queue_key] = deque()
            
            self.normal_queues[queue_key].append(ticket_id)

        return ticket

    def serve_next(self, office_id: str, service: str) -> Optional[Ticket]:
        """
        O(log n) - Serve next customer.
        - Priority Queue (Heap) is checked first: O(log n) pop
        - Normal Queue (Deque) is checked second: O(1) popleft
        """
        try:
            service_enum = ServiceType(service)
        except ValueError:
            return None

        queue_key = (office_id, service_enum.value)
        next_ticket_id = None

        # 1. Try Priority Heap
        if queue_key in self.priority_heaps and self.priority_heaps[queue_key]:
            while self.priority_heaps[queue_key]:
                _, _, tid = heapq.heappop(self.priority_heaps[queue_key])
                if tid in self.active_tickets_by_id:
                    next_ticket_id = tid
                    break
        
        # 2. Try Normal Deque if no priority customer found
        if not next_ticket_id and queue_key in self.normal_queues:
            while self.normal_queues[queue_key]:
                tid = self.normal_queues[queue_key].popleft()
                if tid in self.active_tickets_by_id:
                    next_ticket_id = tid
                    break
        
        if not next_ticket_id:
            return None # Queue empty

        # Process the served ticket
        ticket = self.active_tickets_by_id[next_ticket_id]
        ticket.status = "SERVED"
        
        # Clean up Lookups O(1)
        del self.active_tickets_by_id[next_ticket_id]
        
        user_key = (office_id, ticket.customer.user_id, service_enum.value)
        if user_key in self.active_ticket_by_user:
            del self.active_ticket_by_user[user_key]

        # Update Analytics
        wait_duration = (get_current_time() - ticket.issued_at).total_seconds() / 60.0
        
        if service not in self.served_count:
            self.served_count[service] = 0
            self.total_wait_time_sum[service] = 0.0
            
        self.served_count[service] += 1
        self.total_wait_time_sum[service] += wait_duration

        return ticket

    def get_position(self, ticket_id: str) -> Tuple[int, int]:
        """
        O(n) - Calculate position and estimated wait time.
        We must iterate active structures to count people ahead.
        Returns: (position_index_1_based, estimated_minutes)
        """
        if ticket_id not in self.active_tickets_by_id:
            return -1, 0

        my_ticket = self.active_tickets_by_id[ticket_id]
        queue_key = (my_ticket.office_id, my_ticket.service.value)
        
        position = 0
        est_minutes = 0

        is_priority_me = my_ticket.priority_level > 0
        my_heap_criteria = None

        heap_list = self.priority_heaps.get(queue_key, [])
        
        # 1. Analyze Heap (Priority Customers)
        if heap_list:
            if is_priority_me:
                # Find myself first to get comparison criteria O(n)
                for entry in heap_list:
                    if entry[2] == ticket_id:
                        my_heap_criteria = entry # (-p, c, id)
                        break
                
                if my_heap_criteria:
                    # Count everyone strictly smaller (better priority/earlier)
                    for entry in heap_list:
                        if entry[2] == ticket_id: continue
                        if entry < my_heap_criteria:
                             tid = entry[2]
                             if tid in self.active_tickets_by_id:
                                other_ticket = self.active_tickets_by_id[tid]
                                position += 1
                                est_minutes += other_ticket.expected_minutes
            else:
                # I am Normal. ALL valid priority customers are ahead of me.
                for _, _, tid in heap_list:
                    if tid in self.active_tickets_by_id:
                        other_ticket = self.active_tickets_by_id[tid]
                        position += 1
                        est_minutes += other_ticket.expected_minutes

        # 2. Analyze Deque (Normal Customers)
        # Only relevant if I am normal. Priority customers skip line.
        if not is_priority_me:
            normal_dq = self.normal_queues.get(queue_key, deque())
            found_self = False
            for tid in normal_dq:
                if tid == ticket_id:
                    found_self = True
                    break
                
                if tid in self.active_tickets_by_id:
                    other_ticket = self.active_tickets_by_id[tid]
                    position += 1
                    est_minutes += other_ticket.expected_minutes
            
        return position + 1, est_minutes
