from enum import Enum
from pm4py.objects.ocel.obj import OCEL
import networkx as nx
from typing import Optional, Dict, Any
from pm4py.util import exec_utils


class Parameters(Enum):
    INCLUDE_DF = "include_df"


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

    G = nx.DiGraph()

    stream = ocel.events.to_dict("records")
    for ev in stream:
        ev["type"] = "event"
        G.add_node(ev[ocel.event_id_column], attr=ev)

    stream = ocel.objects.to_dict("records")
    for obj in stream:
        obj["type"] = "object"
        G.add_node(obj[ocel.object_id_column], attr=obj)

    relations = ocel.relations[[ocel.event_id_column, ocel.object_id_column]]
    stream = relations.to_dict("records")
    for rel in stream:
        G.add_edge(rel[ocel.event_id_column], rel[ocel.object_id_column], attr={"type": "REL"})

    if include_df:
        lifecycle = relations.groupby(ocel.object_id_column).agg(list).to_dict()[ocel.event_id_column]
        for obj in lifecycle:
            lif = lifecycle[obj]
            for i in range(len(lif)-1):

                G.add_edge(lif[i], lif[i+1], attr={"type": "DF", "object": obj})

    return G
