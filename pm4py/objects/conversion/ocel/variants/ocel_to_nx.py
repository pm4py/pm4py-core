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

from enum import Enum
from pm4py.objects.ocel.obj import OCEL
import networkx as nx
from typing import Optional, Dict, Any
from pm4py.util import exec_utils
from pm4py.objects.conversion.log.variants import to_event_stream
from copy import copy


class Parameters(Enum):
    INCLUDE_DF = "include_df"
    INCLUDE_OBJECT_CHANGES = "include_object_changes"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> nx.DiGraph:
    """
    Converts an OCEL to a NetworkX DiGraph object.
    The nodes are the events and objects of the OCEL.
    The edges are of two different types:
    - relation edges, connecting an event to its related objects
    - directly-follows edges, connecting an event to a following event (in the lifecycle of one of the related objects)

    Parameters
    ---------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.INCLUDE_DF => include the directly-follows relationship

    Returns
    ---------------
    G
        NetworkX DiGraph
    """
    if parameters is None:
        parameters = {}

    include_df = exec_utils.get_param_value(Parameters.INCLUDE_DF, parameters, True)
    include_object_changes = exec_utils.get_param_value(Parameters.INCLUDE_OBJECT_CHANGES, parameters, True)

    G = nx.DiGraph()

    stream = ocel.events.to_dict("records")
    stream = to_event_stream.__postprocess_stream(stream)
    for ev in stream:
        ev["type"] = "EVENT"
        G.add_node(ev[ocel.event_id_column], attr=ev)

    stream = ocel.objects.to_dict("records")
    stream = to_event_stream.__postprocess_stream(stream)
    for obj in stream:
        obj["type"] = "OBJECT"
        G.add_node(obj[ocel.object_id_column], attr=obj)

    rel_cols = {ocel.event_id_column, ocel.object_id_column, ocel.qualifier}

    relations = ocel.relations[list(rel_cols)]
    stream = relations.to_dict("records")
    for rel in stream:
        qualifier = rel[ocel.qualifier]
        if qualifier is None:
            qualifier = ''
        G.add_edge(rel[ocel.event_id_column], rel[ocel.object_id_column], attr={"type": "E2O", "qualifier": qualifier})

    obj_relations = ocel.o2o[[ocel.object_id_column, ocel.object_id_column + '_2', ocel.qualifier]]
    stream = obj_relations.to_dict("records")
    for rel in stream:
        qualifier = rel[ocel.qualifier]
        if qualifier is None:
            qualifier = ''
        G.add_edge(rel[ocel.object_id_column], rel[ocel.object_id_column + '_2'],
                   attr={"type": "O2O", "qualifier": qualifier})

    if include_df:
        lifecycle = relations.groupby(ocel.object_id_column).agg(list).to_dict()[ocel.event_id_column]
        for obj in lifecycle:
            lif = lifecycle[obj]
            for i in range(len(lif) - 1):
                G.add_edge(lif[i], lif[i + 1], attr={"type": "DF", "object": obj})

    if include_object_changes:
        object_changes = ocel.object_changes.to_dict("records")
        for i in range(len(object_changes)):
            change_id = "@@change##%d" % i
            change_dict = copy(object_changes[i])
            change_dict["type"] = "CHANGE"
            G.add_node(change_id, attr=change_dict)
            G.add_edge(change_id, object_changes[i][ocel.object_id_column], attr={"type": "CHANGE"})

    return G
