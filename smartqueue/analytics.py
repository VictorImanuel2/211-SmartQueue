from typing import List, Tuple
from .queues import QueueManager

def rank_services_by_avg_wait(manager: QueueManager) -> List[Tuple[str, float]]:
    """
    O(n log n) - Ranks services by average wait time (descending).
    
    Why O(n log n)?
    - Iterating services is O(n)
    - Python's generic sort (Timsort) is O(n log n)
    """
    stats = []
    
    # O(n) to build the list
    for service, count in manager.served_count.items():
        total_time = manager.total_wait_time_sum.get(service, 0.0)
        avg_wait = total_time / count if count > 0 else 0.0
        stats.append((service, avg_wait))
    
    # O(n log n) to sort
    # Sort by avg_wait descending
    stats.sort(key=lambda x: x[1], reverse=True)
    
    return stats
