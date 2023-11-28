from datetime import datetime, timezone
from pm4py.util import constants


def fix_dataframe_column(serie):
    if constants.ENABLE_DATETIME_COLUMNS_AWARE:
        # Convert to UTC if the datetime is naive
        if serie.dt.tz is None:
            serie = serie.dt.tz_localize('UTC')
        else:
            # Convert to UTC if it's not already in UTC
            serie = serie.dt.tz_convert('UTC')
    else:
        serie = serie.dt.tz_localize(None)

    return serie


def fix_naivety(dt):
    if dt.tzinfo is None and constants.ENABLE_DATETIME_COLUMNS_AWARE:
        dt = dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo is not None and not constants.ENABLE_DATETIME_COLUMNS_AWARE:
        dt = dt.replace(tzinfo=None)

    return dt


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
    dt = datetime.fromisoformat(dt)

    return fix_naivety(dt)
