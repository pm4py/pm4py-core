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
from pm4py.util import pandas_utils


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

    ordered_events = parameters["ordered_events"] if "ordered_events" in parameters else ocel.events[ocel.event_id_column].to_numpy()

    activities = pandas_utils.format_unique(ocel.events[ocel.event_activity].unique())

    data = []
    feature_names = ["@@event_act_"+act for act in activities]

    events_activities = ocel.events[[ocel.event_id_column, ocel.event_activity]].to_dict("records")
    events_activities = {x[ocel.event_id_column]: x[ocel.event_activity] for x in events_activities}

    for ev in ordered_events:
        data.append([0.0] * len(activities))
        data[-1][activities.index(events_activities[ev])] = 1.0

    return data, feature_names
