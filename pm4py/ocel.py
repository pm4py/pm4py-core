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

from typing import List, Dict, Collection, Set, Tuple

import pandas as pd

from pm4py.objects.ocel.obj import OCEL


def ocel_get_object_types(ocel: OCEL) -> List[str]:
    """
    Gets the list of object types contained in the object-centric event log
    (e.g., ["order", "item", "delivery"]).

    Parameters
    -----------------
    ocel
        Object-centric event log

    Returns
    ----------------
    object_types_list
        List of object types contained in the event log (e.g., ["order", "item", "delivery"])
    """
    return list(ocel.objects[ocel.object_type_column].unique())


def ocel_get_attribute_names(ocel: OCEL) -> List[str]:
    """
    Gets the list of attributes at the event and the object level of an object-centric event log
    (e.g. ["cost", "amount", "name"])

    Parameters
    -------------------
    ocel
        Object-centric event log

    Returns
    -------------------
    attributes_list
        List of attributes at the event and object level (e.g. ["cost", "amount", "name"])
    """
    from pm4py.objects.ocel.util import attributes_names
    return attributes_names.get_attribute_names(ocel)


def ocel_flattening(ocel: OCEL, object_type: str) -> pd.DataFrame:
    """
    Flattens the object-centric event log to a traditional event log with the choice of an object type.
    In the flattened log, the objects of a given object type are the cases, and each case
    contains the set of events related to the object.

    Parameters
    -------------------
    ocel
        Object-centric event log
    object_type
        Object type

    Returns
    ------------------
    dataframe
        Flattened log in the form of a Pandas dataframe
    """
    from pm4py.objects.ocel.util import flattening
    return flattening.flatten(ocel, object_type)




def ocel_object_type_activities(ocel: OCEL) ->  Dict[str, Collection[str]]:
    """
    Gets the set of activities performed for each object type

    Parameters
    ----------------
    ocel
        Object-centric event log

    Returns
    ----------------
    dict
        A dictionary having as key the object types and as values the activities performed for that object type
    """
    from pm4py.statistics.ocel import ot_activities

    return ot_activities.get_object_type_activities(ocel)


def ocel_objects_ot_count(ocel: OCEL) -> Dict[str, Dict[str, int]]:
    """
    Counts for each event the number of related objects per type

    Parameters
    -------------------
    ocel
        Object-centric Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID => the event identifier to be used
        - Parameters.OBJECT_ID => the object identifier to be used
        - Parameters.OBJECT_TYPE => the object type to be used

    Returns
    -------------------
    dict_ot
        Dictionary associating to each event identifier a dictionary with the number of related objects
    """
    from pm4py.statistics.ocel import objects_ot_count

    return objects_ot_count.get_objects_ot_count(ocel)


def ocel_temporal_summary(ocel: OCEL) -> pd.DataFrame:
    """
    Returns the ``temporal summary'' from an object-centric event log.
    The temporal summary aggregates all the events performed in the same timestamp,
    and reports the set of activities and the involved objects.

    :param ocel: object-centric event log
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        temporal_summary = pm4py.ocel_temporal_summary(ocel)
    """
    gdf = ocel.relations.groupby(ocel.event_timestamp)
    act_comb = gdf[ocel.event_activity].agg(set).to_frame()
    obj_comb = gdf[ocel.object_id_column].agg(set).to_frame()
    temporal_summary = act_comb.join(obj_comb).reset_index()
    return temporal_summary


def ocel_objects_summary(ocel: OCEL) -> pd.DataFrame:
    """
    Gets the objects summary of an object-centric event log

    :param ocel: object-centric event log
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        objects_summary = pm4py.ocel_objects_summary(ocel)
    """
    gdf = ocel.relations.groupby(ocel.object_id_column)
    act_comb = gdf[ocel.event_activity].agg(list).to_frame().rename(columns={ocel.event_activity: "activities_lifecycle"})
    lif_start_tim = gdf[ocel.event_timestamp].min().to_frame().rename(columns={ocel.event_timestamp: "lifecycle_start"})
    lif_end_tim = gdf[ocel.event_timestamp].max().to_frame().rename(columns={ocel.event_timestamp: "lifecycle_end"})
    objects_summary = act_comb.join(lif_start_tim)
    objects_summary = objects_summary.join(lif_end_tim)
    objects_summary = objects_summary.reset_index()
    objects_summary["lifecycle_duration"] = (objects_summary["lifecycle_end"] - objects_summary["lifecycle_start"]).astype('timedelta64[s]')
    ev_rel_obj = ocel.relations.groupby(ocel.event_id_column)[ocel.object_id_column].apply(list).to_dict()
    objects_ids = set(ocel.objects[ocel.object_id_column].unique())
    graph = {o: set() for o in objects_ids}
    for ev in ev_rel_obj:
        rel_obj = ev_rel_obj[ev]
        for o1 in rel_obj:
            for o2 in rel_obj:
                if o1 != o2:
                    graph[o1].add(o2)
    objects_summary["interacting_objects"] = objects_summary[ocel.object_id_column].map(graph)
    return objects_summary


def discover_objects_graph(ocel: OCEL, graph_type: str = "object_interaction") -> Set[Tuple[str, str]]:
    """
    Discovers an object graph from the provided object-centric event log

    :param ocel: object-centric event log
    :param graph_type: type of graph to consider (object_interaction, object_descendants, object_inheritance, object_cobirth, object_codeath)
    :rtype: ``Dict[str, Any]``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('trial.ocel')
        obj_graph = pm4py.ocel_discover_objects_graph(ocel, graph_type='object_interaction')
    """
    if graph_type == "object_interaction":
        from pm4py.algo.transformation.ocel.graphs import object_interaction_graph
        return object_interaction_graph.apply(ocel)
    elif graph_type == "object_descendants":
        from pm4py.algo.transformation.ocel.graphs import object_descendants_graph
        return object_descendants_graph.apply(ocel)
    elif graph_type == "object_inheritance":
        from pm4py.algo.transformation.ocel.graphs import object_inheritance_graph
        return object_inheritance_graph.apply(ocel)
    elif graph_type == "object_cobirth":
        from pm4py.algo.transformation.ocel.graphs import object_cobirth_graph
        return object_cobirth_graph.apply(ocel)
    elif graph_type == "object_codeath":
        from pm4py.algo.transformation.ocel.graphs import object_codeath_graph
        return object_codeath_graph.apply(ocel)
