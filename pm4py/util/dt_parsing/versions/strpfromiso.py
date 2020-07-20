from datetime import datetime

# NB: Compatible only from Python 3.7 onwards!!!


def apply(dt):
    """
    Parses the string to a datetime object (uses Python default strptime)

    Parameters
    --------------
    dt
        Date string

    Returns
    --------------
    datetime
        Datetime object
    """
    if dt.endswith("Z"):
        # Z at the end of date means UTC, but that is not ISO format.
        # Replace "Z" with "+00:00" that is also UTC
        dt = dt[:-1] + "+00:00"
    return datetime.fromisoformat(dt)
