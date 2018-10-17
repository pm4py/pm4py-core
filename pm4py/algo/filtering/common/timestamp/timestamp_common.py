from datetime import datetime


def get_dt_from_string(dt):
    """
    If the date is expressed as string, do the conversion to a datetime.datetime object

    Parameters
    -----------
    dt
        Date (string or datetime.datetime)

    Returns
    -----------
    dt
        Datetime object
    """
    if type(dt) is str:
        return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
