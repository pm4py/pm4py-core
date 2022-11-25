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
__doc__ = """
The ``pm4py.ocel`` module contains the object-centric process mining features offered in ``pm4py``
"""

from typing import List, Dict, Collection, Any, Optional, Set, Tuple

import pandas as pd

from pm4py.objects.ocel.obj import OCEL
from pm4py.util import constants

def ocel_get_object_types(ocel: OCEL) -> List[str]:
    """
    Gets the list of object types contained in the object-centric event log
    (e.g., ["order", "item", "delivery"]).

    :param ocel: object-centric event log
    :rtype: ``List[str]``

    .. code-block:: python3

        import pm4py

        object_types = pm4py.ocel_get_object_types(ocel)
    """
    return list(ocel.objects[ocel.object_type_column].unique())


def ocel_get_attribute_names(ocel: OCEL) -> List[str]:
    """
    Gets the list of attributes at the event and the object level of an object-centric event log
    (e.g. ["cost", "amount", "name"])

    :param ocel: object-centric event log
    :rtype: ``List[str]``

    .. code-block:: python3

        import pm4py

        attribute_names = pm4py.ocel_get_attribute_names(ocel)
    """
    from pm4py.objects.ocel.util import attributes_names
    return attributes_names.get_attribute_names(ocel)


def ocel_flattening(ocel: OCEL, object_type: str) -> pd.DataFrame:
    """
    Flattens the object-centric event log to a traditional event log with the choice of an object type.
    In the flattened log, the objects of a given object type are the cases, and each case
    contains the set of events related to the object.

    :param ocel: object-centric event log
    :param object_type: object type
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        event_log = pm4py.ocel_flattening(ocel, 'items')
    """
    from pm4py.objects.ocel.util import flattening
    return flattening.flatten(ocel, object_type)


def ocel_object_type_activities(ocel: OCEL) -> Dict[str, Collection[str]]:
    """
    Gets the set of activities performed for each object type

    :param ocel: object-centric event log
    :rtype: ``Dict[str, Collection[str]]``

    .. code-block:: python3

        import pm4py

        ot_activities = pm4py.ocel_object_type_activities(ocel)
    """
    from pm4py.statistics.ocel import ot_activities

    return ot_activities.get_object_type_activities(ocel)


def ocel_objects_ot_count(ocel: OCEL) -> Dict[str, Dict[str, int]]:
    """
    Counts for each event the number of related objects per type

    :param ocel: object-centric event log
    :rtype: ``Dict[str, Dict[str, int]]``

    .. code-block:: python3

        import pm4py

        objects_ot_count = pm4py.ocel_objects_ot_count(ocel)
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


def ocel_objects_interactions_summary(ocel: OCEL) -> pd.DataFrame:
    """
    Gets the objects interactions summary of an object-centric event log.
    The objects interactions summary has a row for every combination (event, related object, other related object).
    Properties such as the activity of the event, and the object types of the two related objects, are included.

    :param ocel: object-centric event log
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        interactions_summary = pm4py.ocel_objects_interactions_summary(ocel)
    """
    obj_types = ocel.objects.groupby(ocel.object_id_column)[ocel.object_type_column].first().to_dict()
    eve_activities = ocel.events.groupby(ocel.event_id_column)[ocel.event_activity].first().to_dict()
    ev_rel_obj = ocel.relations.groupby(ocel.event_id_column)[ocel.object_id_column].apply(list).to_dict()
    stream = []
    for ev in ev_rel_obj:
        rel_obj = ev_rel_obj[ev]
        for o1 in rel_obj:
            for o2 in rel_obj:
               if o1 != o2:
                   stream.append({ocel.event_id_column: ev, ocel.event_activity: eve_activities[ev],
                                  ocel.object_id_column: o1, ocel.object_type_column: obj_types[o1],
                                  ocel.object_id_column+"_2": o2, ocel.object_type_column+"_2": obj_types[o2]})

    import pandas as pd
    return pd.DataFrame(stream)


def discover_ocdfg(ocel: OCEL, business_hours=False, business_hour_slots=constants.DEFAULT_BUSINESS_HOUR_SLOTS) -> Dict[str, Any]:
    """
    Discovers an OC-DFG from an object-centric event log.

    Object-centric directly-follows multigraphs are a composition of directly-follows graphs for the single object type, which can be annotated with different metrics considering the entities of an object-centric event log (i.e., events, unique objects, total objects).

    Reference paper:
    Berti, Alessandro, and Wil van der Aalst. "Extracting multiple viewpoint models from relational databases." Data-Driven Process Discovery and Analysis. Springer, Cham, 2018. 24-51.

    :param ocel: object-centric event log
    :param business_hours: boolean value that enables the usage of the business hours
    :param business_hour_slots: work schedule of the company, provided as a list of tuples where each tuple represents one time slot of business hours. One slot i.e. one tuple consists of one start and one end time given in seconds since week start, e.g. [(7 * 60 * 60, 17 * 60 * 60), ((24 + 7) * 60 * 60, (24 + 12) * 60 * 60), ((24 + 13) * 60 * 60, (24 + 17) * 60 * 60),] meaning that business hours are Mondays 07:00 - 17:00 and Tuesdays 07:00 - 12:00 and 13:00 - 17:00

    :rtype: ``Dict[str, Any]``

    .. code-block:: python3

        import pm4py

        ocdfg = pm4py.discover_ocdfg(ocel)
    """
    parameters = {}
    parameters["business_hours"] = business_hours
    parameters["business_hour_slots"] = business_hour_slots
    from pm4py.algo.discovery.ocel.ocdfg import algorithm as ocdfg_discovery
    return ocdfg_discovery.apply(ocel, parameters=parameters)


def discover_oc_petri_net(ocel: OCEL) -> Dict[str, Any]:
    """
    Discovers an object-centric Petri net from the provided object-centric event log.

    Reference paper: van der Aalst, Wil MP, and Alessandro Berti. "Discovering object-centric Petri nets." Fundamenta informaticae 175.1-4 (2020): 1-40.

    :param ocel: object-centric event log
    :rtype: ``Dict[str, Any]``

    .. code-block:: python3

        import pm4py

        ocpn = pm4py.discover_oc_petri_net(ocel)
    """
    from pm4py.algo.discovery.ocel.ocpn import algorithm as ocpn_discovery
    return ocpn_discovery.apply(ocel)


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


def sample_ocel_objects(ocel: OCEL, num_objects: int) -> OCEL:
    """
    Given an object-centric event log, returns a sampled event log with a subset of the objects
    that is chosen in a random way.
    Only the events related to at least one of these objects are filtered from the event log.
    As a note, the relationships between the different objects are probably going to be ruined by
    this sampling.

    :param ocel: Object-centric event log
    :param num_objects: Number of objects of the object-centric event log
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('trial.ocel')
        sampled_ocel = pm4py.sample_ocel_objects(ocel, 50) # keeps only 50 random objects
    """
    from pm4py.objects.ocel.util import sampling
    return sampling.sample_ocel_objects(ocel, parameters={"num_entities": num_objects})


def sample_ocel_connected_components(ocel: OCEL, connected_components: int = 1) -> OCEL:
    """
    Given an object-centric event log, returns a sampled event log with a subset of the executions.
    The number of considered connected components need to be specified by the user.

    :param ocel: Object-centric event log
    :param connected_components: Number of connected components to pick from the OCEL
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('trial.ocel')
        sampled_ocel = pm4py.sample_ocel_connected_components(ocel, 5) # keeps only 5 connected components
    """
    from pm4py.algo.transformation.ocel.split_ocel import algorithm
    ocel_splits = algorithm.apply(ocel)
    events = None
    objects = None
    relations = None
    ocel_splits = sorted(list(ocel_splits), key=lambda x: (len(x.events), len(x.relations)))
    i = 0
    while i < min(connected_components, len(ocel_splits)):
        cc = ocel_splits[i]
        if events is None:
            events = cc.events
            objects = cc.objects
            relations = cc.relations
        else:
            events = pd.concat([events, cc.events])
            objects = pd.concat([objects, cc.objects])
            relations = pd.concat([relations, cc.relations])
        i = i + 1

    return OCEL(events, objects, relations)


def ocel_drop_duplicates(ocel: OCEL) -> OCEL:
    """
    Drop relations between events and objects happening at the same time,
    with the same activity, to the same object identifier.
    This ends up cleaning the OCEL from duplicate events.

    :param ocel: object-centric event log
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('trial.ocel')
        ocel = pm4py.ocel_drop_duplicates(ocel)

    """
    from pm4py.objects.ocel.util import filtering_utils
    ocel.relations = ocel.relations.drop_duplicates(
        subset=[ocel.event_activity, ocel.event_timestamp, ocel.object_id_column])
    ocel = filtering_utils.propagate_relations_filtering(ocel)
    return ocel


def ocel_merge_duplicates(ocel: OCEL, have_common_object: Optional[bool]=False) -> OCEL:
    """
    Merge events in the OCEL that happen with the same activity at the same timestamp

    :param ocel: object-centric event log
    :param have_common_object: impose the additional merge condition that the two events should happen at the same
                                timestamp.
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('trial.ocel')
        ocel = pm4py.ocel_merge_duplicates(ocel)
    """
    import copy
    import uuid
    relations = copy.copy(ocel.relations)
    if have_common_object:
        relations["@@groupn"] = relations.groupby([ocel.object_id_column, ocel.event_activity, ocel.event_timestamp]).ngroup()
    else:
        relations["@@groupn"] = relations.groupby([ocel.event_activity, ocel.event_timestamp]).ngroup()

    group_size = relations["@@groupn"].value_counts().to_dict()
    relations["@@groupsize"] = relations["@@groupn"].map(group_size)
    relations = relations.sort_values(["@@groupsize", "@@groupn"], ascending=False)
    val_corr = {x: str(uuid.uuid4()) for x in relations["@@groupn"].unique()}
    relations = relations.groupby(ocel.event_id_column).first()["@@groupn"].to_dict()
    relations = {x: val_corr[y] for x, y in relations.items()}

    ocel.events[ocel.event_id_column] = ocel.events[ocel.event_id_column].map(relations)
    ocel.relations[ocel.event_id_column] = ocel.relations[ocel.event_id_column].map(relations)

    ocel.events = ocel.events.drop_duplicates(subset=[ocel.event_id_column])
    ocel.relations = ocel.relations.drop_duplicates(subset=[ocel.event_id_column, ocel.object_id_column])

    return ocel



def ocel_sort_by_additional_column(ocel: OCEL, additional_column: str, primary_column: str = "ocel:timestamp") -> OCEL:
    """
    Sorts the OCEL not only based on the timestamp column and the index,
    but using an additional sorting column that further determines the order of
    the events happening at the same timestamp.

    :param ocel: object-centric event log
    :param additional_column: additional column to use for the sorting
    :param primary_column: primary column to be used for the sorting (default: ocel:timestamp)
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('trial.ocel')
        ocel = pm4py.ocel_sort_by_additional_column(ocel, 'ordering')

    """
    ocel.events["@@index"] = ocel.events.index
    ocel.events = ocel.events.sort_values([primary_column, additional_column, "@@index"])
    del ocel.events["@@index"]
    ocel.events.reset_index(inplace=True, drop=True)
    return ocel


def ocel_add_index_based_timedelta(ocel: OCEL) -> OCEL:
    """
    Adds a small time-delta to the timestamp column based on the current index of the event.
    This ensures the correct ordering of the events in any object-centric process mining
    solution.

    :param ocel: object-centric event log
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('trial.ocel')
        ocel = pm4py.ocel_add_index_based_timedelta(ocel)

    """
    from datetime import timedelta
    eids = ocel.events[ocel.event_id_column].to_list()
    eids = {eids[i]: timedelta(milliseconds=i) for i in range(len(eids))}
    ocel.events["@@timedelta"] = ocel.events[ocel.event_id_column].map(eids)
    ocel.relations["@@timedelta"] = ocel.relations[ocel.event_id_column].map(eids)
    ocel.events[ocel.event_timestamp] = ocel.events[ocel.event_timestamp] + ocel.events["@@timedelta"]
    ocel.relations[ocel.event_timestamp] = ocel.relations[ocel.event_timestamp] + ocel.relations["@@timedelta"]
    del ocel.events["@@timedelta"]
    del ocel.relations["@@timedelta"]
    return ocel
