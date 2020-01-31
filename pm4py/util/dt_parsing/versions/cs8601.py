import ciso8601


def apply(dt):
    """
    Parses the string to a datetime object (use ciso8601)

    Parameters
    --------------
    dt
        Date string

    Returns
    --------------
    datetime
        Datetime object
    """
    return ciso8601.parse_datetime(dt)
