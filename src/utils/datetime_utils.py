"""
Utility functions for parsing and formatting datetimes.
"""

from datetime import datetime, timezone

from dateutil import parser as date_parser
from dateutil.parser import ParserError


def parse_datetime(value: str | None) -> datetime | None:
    """
    Parse a datetime string into a timezone-aware UTC datetime.

    Args:
        value:
            Datetime string to parse.

    Returns:
        A timezone-aware UTC datetime, or None if parsing fails.
    """
    if not value:
        return None

    try:
        dt = date_parser.parse(value)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(timezone.utc)

    except (ParserError, TypeError, ValueError):
        return None


def datetime_to_iso(value: datetime) -> str:
    """
    Convert a datetime to an ISO 8601 string in UTC.

    Args:
        value:
            Datetime to serialize.

    Returns:
        ISO 8601 representation in UTC.
    """
    return value.astimezone(timezone.utc).isoformat()

def utc_now() -> datetime:
    """
    Return the current UTC time as a timezone-aware datetime.
    """
    return datetime.now(timezone.utc)

def get_current_day() -> str:
    """
    Returns today's date in ISO format (YYYY-MM-DD).
    """
    return utc_now().date().isoformat()