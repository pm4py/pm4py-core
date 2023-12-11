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
from typing import Optional, Dict, Any, Set, Tuple


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Set[Tuple[str, str]]:
    """
    Calculates the object descendant graph.
    This is calculated as follows:
    - Given the set of objects related to an event, they belong to two different categories:
        - The "seen" objects (they have appeared in some earlier event)
        - The "unseen" objects (they appear for the first time in the current event).
    - Every "seen" object is connected to every "unseen" object.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm

    Returns
    ------------------
    object_descendant_graph
        Object descendant graph (directed)
    """
    if parameters is None:
        parameters = {}

    graph = set()

    ordered_events = ocel.events[ocel.event_id_column].to_numpy()
    ev_rel_obj = ocel.relations.groupby(ocel.event_id_column)[ocel.object_id_column].agg(list).to_dict()
    set_objects = set()

    for ev in ordered_events:
        rel_obj = ev_rel_obj[ev]
        rel_obj_seen = {x for x in rel_obj if x in set_objects}
        rel_obj_unseen = {x for x in rel_obj if x not in rel_obj_seen}
        if rel_obj_seen and rel_obj_unseen:
            for o1 in rel_obj_seen:
                for o2 in rel_obj_unseen:
                    graph.add((o1, o2))
        for obj in rel_obj_unseen:
            set_objects.add(obj)

    return graph
