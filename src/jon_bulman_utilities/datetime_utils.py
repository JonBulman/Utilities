# date and time utilities
from datetime import datetime
from zoneinfo import ZoneInfo


def convert_utc_to_local(date, time):
    # date = "2024-08-07"
    # time = "13:45"

    utc_format = "%Y-%m-%d %H:%M"
    utc_string = f"{date} {time}"

    # Parse as naive UTC, then attach UTC tzinfo
    utc_dt = datetime.strptime(utc_string, utc_format).replace(tzinfo=ZoneInfo("UTC"))

    # Convert to Europe/London (handles GMT/BST automatically)
    local_dt = utc_dt.astimezone(ZoneInfo("Europe/London"))

    return local_dt

def parse_date(date_str, *, end_of_day=False):
    """Parse yyyy-mm-dd into a timezone-aware datetime."""
    try:
        y, m, d = map(int, date_str.split("-"))
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}")

    if end_of_day:
        return datetime(y, m, d, 23, 30, 0, tzinfo=ZoneInfo("Europe/London"))
    else:
        return datetime(y, m, d, 0, 0, 0, tzinfo=ZoneInfo("Europe/London"))