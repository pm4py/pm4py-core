__doc__ = """
The ``pm4py.ocel`` module contains the object-centric process mining features offered in ``pm4py``
"""

from typing import List, Dict, Collection, Any, Optional, Set, Tuple

import pandas as pd

from pm4py.objects.ocel.obj import OCEL


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


def discover_ocdfg(ocel: OCEL, business_hours=False, worktiming=[7, 17], weekends=[6, 7]) -> Dict[str, Any]:
    """
    Discovers an OC-DFG from an object-centric event log.

    Object-centric directly-follows multigraphs are a composition of directly-follows graphs for the single object type, which can be annotated with different metrics considering the entities of an object-centric event log (i.e., events, unique objects, total objects).

    Reference paper:
    Berti, Alessandro, and Wil van der Aalst. "Extracting multiple viewpoint models from relational databases." Data-Driven Process Discovery and Analysis. Springer, Cham, 2018. 24-51.

    :param ocel: object-centric event log
    :param business_hours: boolean value that enables the usage of the business hours
    :param worktiming: (if business hours are in use) work timing during the day (default: [7, 17])
    :param weekends: (if business hours are in use) weekends (default: [6, 7])
    :rtype: ``Dict[str, Any]``

    .. code-block:: python3

        import pm4py

        ocdfg = pm4py.discover_ocdfg(ocel)
    """
    parameters = {}
    parameters["business_hours"] = business_hours
    parameters["worktiming"] = worktiming
    parameters["weekends"] = weekends
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
