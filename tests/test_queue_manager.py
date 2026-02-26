import unittest
from smartqueue.queues import QueueManager
from smartqueue.models import Ticket

class TestQueueManager(unittest.TestCase):
    def setUp(self):
        self.manager = QueueManager()

    def test_issue_ticket_unique_user(self):
        """Test that a user cannot have two active tickets for the same service."""
        self.manager.issue_ticket("u1", "Alice", "passport")
        with self.assertRaises(ValueError):
            self.manager.issue_ticket("u1", "Alice", "passport")

    def test_fifo_ordering_normal(self):
        """Test FIFO behavior for normal customers."""
        t1 = self.manager.issue_ticket("u1", "A", "passport", priority_level=0)
        t2 = self.manager.issue_ticket("u2", "B", "passport", priority_level=0)
        
        served1 = self.manager.serve_next("default", "passport")
        self.assertEqual(served1.ticket_id, t1.ticket_id)
        
        served2 = self.manager.serve_next("default", "passport")
        self.assertEqual(served2.ticket_id, t2.ticket_id)

    def test_priority_ordering(self):
        """Test that priority customers skip the line."""
        # 1. Normal customer arrives first
        t1 = self.manager.issue_ticket("u1", "Normal", "passport", priority_level=0)
        
        # 2. Priority customer arrives later
        t2 = self.manager.issue_ticket("u2", "Vip", "passport", priority_level=10)
        
        # 3. Another Priority customer arrives (lower priority than VIP but higher than Normal)
        t3 = self.manager.issue_ticket("u3", "Urgent", "passport", priority_level=5)

        # Expect order: VIP (10) -> Urgent (5) -> Normal (0)
        served1 = self.manager.serve_next("default", "passport")
        self.assertEqual(served1.ticket_id, t2.ticket_id, "VIP should be first")

        served2 = self.manager.serve_next("default", "passport")
        self.assertEqual(served2.ticket_id, t3.ticket_id, "Urgent should be second")

        served3 = self.manager.serve_next("default", "passport")
        self.assertEqual(served3.ticket_id, t1.ticket_id, "Normal should be last")

    def test_position_calculation(self):
        """Test position and wait time estimates."""
        # Add 3 people to passport
        # P1 (Normal) - 10 mins
        t1 = self.manager.issue_ticket("u1", "P1", "passport", priority_level=0, expected_minutes=10)
        # P2 (Priority) - 15 mins
        t2 = self.manager.issue_ticket("u2", "P2", "passport", priority_level=5, expected_minutes=15)
        # P3 (Normal) - 10 mins
        t3 = self.manager.issue_ticket("u3", "P3", "passport", priority_level=0, expected_minutes=10)

        # Check P2 (Priority) - should be #1 (only one in priority heap is self, Wait time 0)
        pos, wait = self.manager.get_position(t2.ticket_id)
        self.assertEqual(pos, 1)
        self.assertEqual(wait, 0) # No one ahead

        # Check P1 (Normal) - should be #2 (behind P2)
        # Wait time = P2 (15)
        pos, wait = self.manager.get_position(t1.ticket_id)
        self.assertEqual(pos, 2)
        self.assertEqual(wait, 15)

        # Check P3 (Normal) - should be #3 (behind P2 and P1)
        # Wait time = P2 (15) + P1 (10) = 25
        pos, wait = self.manager.get_position(t3.ticket_id)
        self.assertEqual(pos, 3)
        self.assertEqual(wait, 25)

if __name__ == "__main__":
    unittest.main()
