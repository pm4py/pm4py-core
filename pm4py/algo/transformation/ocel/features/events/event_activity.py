from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    One-hot encode the activities of an OCEL, assigning to each event its own activity as feature

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

    activities = list(ocel.events[ocel.event_activity].unique())

    data = []
    feature_names = ["@@event_act_"+act for act in activities]

    events_activities = ocel.events[[ocel.event_id_column, ocel.event_activity]].to_dict("records")
    events_activities = {x[ocel.event_id_column]: x[ocel.event_activity] for x in events_activities}

    for ev in ordered_events:
        data.append([0] * len(activities))
        data[-1][activities.index(events_activities[ev])] = 1

    return data, feature_names
