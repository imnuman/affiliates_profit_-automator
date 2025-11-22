"""
Helper functions
"""
import uuid
from datetime import datetime
from typing import Optional


def generate_tracking_id() -> str:
    """Generate a unique tracking ID"""
    return str(uuid.uuid4())[:8].upper()


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"


def calculate_percentage(value: float, total: float) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0.0
    return (value / total) * 100


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def get_start_of_month(date: Optional[datetime] = None) -> datetime:
    """Get start of month for a given date"""
    if date is None:
        date = datetime.utcnow()
    return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def get_date_range_label(start: datetime, end: datetime) -> str:
    """Generate a label for a date range"""
    if start.date() == end.date():
        return start.strftime("%B %d, %Y")
    return f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"
