def derive_end_activities_from_log(log, activity_key):
    """
    Derive end activities from log

    Parameters
    -----------
    log
        Log object
    activity_key
        Activity key

    Returns
    -----------
    e
        End activities
    """
    e = set()
    for t in log:
        if len(t) > 0:
            if activity_key in t[len(t) - 1]:
                e.add(t[len(t) - 1][activity_key])
    return e


def derive_start_activities_from_log(log, activity_key):
    """
    Derive start activities from log

    Parameters
    -----------
    log
        Log object
    activity_key
        Activity key

    Returns
    -----------
    s
        Start activities
    """
    s = set()
    for t in log:
        if len(t) > 0:
            if activity_key in t[0]:
                s.add(t[0][activity_key])
    return s
