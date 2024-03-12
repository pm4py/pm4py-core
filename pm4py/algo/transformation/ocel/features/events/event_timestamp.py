'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
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

    ordered_events = parameters["ordered_events"] if "ordered_events" in parameters else ocel.events[
        ocel.event_id_column].to_numpy()

    data = []
    feature_names = ["@@event_timestamp", "@@event_timestamp_dayofweek", "@@event_timestamp_hour", "@@event_timestamp_month", "@@event_timestamp_day"]

    events_timestamps = ocel.events[[ocel.event_id_column, ocel.event_timestamp]].to_dict("records")
    events_timestamps = {x[ocel.event_id_column]: x[ocel.event_timestamp] for x in events_timestamps}

    for ev in ordered_events:
        data.append([float(events_timestamps[ev].timestamp()), float(events_timestamps[ev].dayofweek), float(events_timestamps[ev].hour), float(events_timestamps[ev].month), float(events_timestamps[ev].day)])

    return data, feature_names
