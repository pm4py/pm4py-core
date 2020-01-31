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
    return datetime.fromisoformat(dt)
