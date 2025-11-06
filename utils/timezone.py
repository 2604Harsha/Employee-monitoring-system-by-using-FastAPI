import pytz
from datetime import datetime

IST = pytz.timezone("Asia/Kolkata")

def now_ist():
    """Return current time in Indian Standard Time (IST)."""
    return datetime.now(IST)

def today_ist_date():
    """Return only the date part in IST timezone."""
    return now_ist().date()

def utc_to_ist(dt):
    """Convert UTC or naive datetime to IST timezone-aware."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # assume it was UTC if naive
        dt = pytz.utc.localize(dt)
    return dt.astimezone(IST)
