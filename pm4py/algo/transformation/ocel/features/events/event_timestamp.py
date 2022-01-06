from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Feature: assigns to each event of the OCEL its own timestamp.

    Parameters
    ----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Extracted feature values
    feature_names
        Feature names
    """
    if parameters is None:
        parameters = {}

    ordered_events = list(ocel.events[ocel.event_id_column])

    data = []
    feature_names = ["@@event_timestamp", "@@event_timestamp_dayofweek", "@@event_timestamp_hour", "@@event_timestamp_month", "@@event_timestamp_day"]

    events_timestamps = ocel.events[[ocel.event_id_column, ocel.event_timestamp]].to_dict("records")
    events_timestamps = {x[ocel.event_id_column]: x[ocel.event_timestamp] for x in events_timestamps}

    for ev in ordered_events:
        data.append([events_timestamps[ev].timestamp(), events_timestamps[ev].dayofweek, events_timestamps[ev].hour, events_timestamps[ev].month, events_timestamps[ev].day])

    return data, feature_names
