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
    Discovers the number of new interactions between the related objects which appears in a given event.

    Parameters
    ---------------
    ocel
        OCEL
    parameters
        Parameters of the method

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

    rel_objs = ocel.relations.groupby(ocel.event_id_column)[ocel.object_id_column].agg(list).to_dict()

    interactions = set()
    data = []
    feature_names = ["@@ev_new_interactions"]

    for ev in ordered_events:
        n = 0
        if ev in rel_objs:
            for o1 in rel_objs[ev]:
                for o2 in rel_objs[ev]:
                    if o1 < o2:
                        if not (o1, o2) in interactions:
                            n = n + 1
        data.append([float(n)])

    return data, feature_names
