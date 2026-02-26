import uuid
from datetime import datetime

def generate_id() -> str:
    """O(1) - Generate a unique ID."""
    return str(uuid.uuid4())[:8].upper()

def get_current_time() -> datetime:
    """O(1) - Get current timestamp."""
    return datetime.now()
