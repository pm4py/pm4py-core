from typing import Optional, Dict, Any, Tuple

import pandas as pd

from pm4py.objects.ocel.obj import OCEL


def get_dataframes_from_ocel(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[
    pd.DataFrame, pd.DataFrame]:
    if parameters is None:
        parameters = {}

    events = ocel.events.copy()
    for col in events.columns:
        if str(events[col].dtype) == "object":
            events[col] = events[col].astype('string')
        elif "date" in str(events[col].dtype):
            events[col] = events[col].apply(pd.Timestamp.isoformat).astype('string')

    objects = ocel.objects.copy()
    for col in objects.columns:
        if str(objects[col].dtype) == "object":
            objects[col] = objects[col].astype('string')
        elif "date" in str(objects[col].dtype):
            objects[col] = objects[col].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    return events, objects
