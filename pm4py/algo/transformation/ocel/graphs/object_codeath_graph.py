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
    Calculates the object codeath graph.

    This is calculated like the object cobirth graph, but visiting the list of events
    in the reverse order.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm

    Returns
    ------------------
    object_codeath_graph
        Object codeath graph (undirected)
    """
    if parameters is None:
        parameters = {}

    graph = set()

    ordered_events = ocel.events[ocel.event_id_column].to_numpy().tolist()
    ev_rel_obj = ocel.relations.groupby(ocel.event_id_column)[ocel.object_id_column].agg(list).to_dict()
    set_objects = set()

    ordered_events.reverse()

    for ev in ordered_events:
        rel_obj = ev_rel_obj[ev]
        rel_obj_seen = {x for x in rel_obj if x in set_objects}
        rel_obj_unseen = {x for x in rel_obj if x not in rel_obj_seen}

        for o1 in rel_obj_unseen:
            for o2 in rel_obj_unseen:
                if o1 < o2:
                    graph.add((o1, o2))

        for obj in rel_obj_unseen:
            set_objects.add(obj)

    return graph
