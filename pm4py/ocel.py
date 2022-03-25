__doc__ = """
"""

from typing import List, Dict, Collection, Any, Optional

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
    # Unit test: YES
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
    # Unit test: YES
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
    # Unit test: YES
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
    # Unit test: YES
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
    # Unit test: YES
    from pm4py.statistics.ocel import objects_ot_count

    return objects_ot_count.get_objects_ot_count(ocel)


def discover_ocdfg(ocel: OCEL, business_hours=False, worktiming=[7, 17], weekends=[6, 7]) -> Dict[str, Any]:
    """
    Discovers an OC-DFG from an object-centric event log.

    Reference paper:
    Berti, Alessandro, and Wil van der Aalst. "Extracting multiple viewpoint models from relational databases." Data-Driven Process Discovery and Analysis. Springer, Cham, 2018. 24-51.


    Parameters
    ----------------
    ocel
        Object-centric event log
    business_hours
        Boolean value that enables the usage of the business hours
    worktiming
        (if business hours are in use) work timing during the day (default: [7, 17])
    weekends
        (if business hours are in use) weekends (default: [6, 7])

    Returns
    ---------------
    ocdfg
        Object-centric directly-follows graph
    """
    # Unit test: YES
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

    Parameters
    -----------------
    ocel
        Object-centric event log

    Returns
    ----------------
    ocpn
        Object-centric Petri net
    """
    # Unit test: YES
    from pm4py.algo.discovery.ocel.ocpn import algorithm as ocpn_discovery
    return ocpn_discovery.apply(ocel)
