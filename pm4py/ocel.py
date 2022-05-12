__doc__ = """
Traditional event logs, used by mainstream process mining techniques, require the events to be related to a case. A case is a set of events for a particular purpose. A case notion is a criteria to assign a case to the events.

However, in real processes this leads to two problems:

* If we consider the Order-to-Cash process, an order could be related to many different deliveries. If we consider the delivery as case notion, the same event of Create Order needs to be replicated in different cases (all the deliveries involving the order). This is called the convergence problem.
* If we consider the Order-to-Cash process, an order could contain different order items, each one with a different lifecycle. If we consider the order as case notion, several instances of the activities for the single items may be contained in the case, and this make the frequency/performance annotation of the process problematic. This is called the divergence problem.

Object-centric event logs relax the assumption that an event is related to exactly one case. Indeed, an event can be related to different objects of different object types.

Essentially, we can describe the different components of an object-centric event log as:

* Events, having an identifier, an activity, a timestamp, a list of related objects and a dictionary of other attributes.
* Objects, having an identifier, a type and a dictionary of other attributes.
* Attribute names, e.g., the possible keys for the attributes of the event/object attribute map.
* Object types, e.g., the possible types for the objects.

In PM4Py, we offer object-centric process mining features:

* `Importing OCELs`_
* `Exporting OCELs`_
* Process Discovery
    * `OC-DFG`_
    * `Object-centric Petri nets`_
* `Flattening`_

.. _Importing OCELs: pm4py.html#pm4py.read.read_ocel
.. _Exporting OCELs: pm4py.html#pm4py.write.write_ocel
.. _OC-DFG: pm4py.html#pm4py.ocel.discover_ocdfg
.. _Object-centric Petri nets: pm4py.html#pm4py.ocel.discover_oc_petri_net
.. _Flattening: pm4py.html#pm4py.ocel.ocel_flattening

"""

from typing import List, Dict, Collection, Any, Optional

import pandas as pd

from pm4py.objects.ocel.obj import OCEL


def ocel_get_object_types(ocel: OCEL) -> List[str]:
    """
    Gets the list of object types contained in the object-centric event log
    (e.g., ["order", "item", "delivery"]).

    :param ocel: object-centric event log
    :rtype: ``List[str]``
    """
    return list(ocel.objects[ocel.object_type_column].unique())


def ocel_get_attribute_names(ocel: OCEL) -> List[str]:
    """
    Gets the list of attributes at the event and the object level of an object-centric event log
    (e.g. ["cost", "amount", "name"])

    :param ocel: object-centric event log
    :rtype: ``List[str]``
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
    """
    from pm4py.objects.ocel.util import flattening
    return flattening.flatten(ocel, object_type)


def ocel_object_type_activities(ocel: OCEL) -> Dict[str, Collection[str]]:
    """
    Gets the set of activities performed for each object type

    :param ocel: object-centric event log
    :rtype: ``Dict[str, Collection[str]]``
    """
    from pm4py.statistics.ocel import ot_activities

    return ot_activities.get_object_type_activities(ocel)


def ocel_objects_ot_count(ocel: OCEL) -> Dict[str, Dict[str, int]]:
    """
    Counts for each event the number of related objects per type

    :param ocel: object-centric event log
    :rtype: ``Dict[str, Dict[str, int]]``
    """
    from pm4py.statistics.ocel import objects_ot_count

    return objects_ot_count.get_objects_ot_count(ocel)


def discover_ocdfg(ocel: OCEL, business_hours=False, worktiming=[7, 17], weekends=[6, 7]) -> Dict[str, Any]:
    """
    Discovers an OC-DFG from an object-centric event log.

    Reference paper:
    Berti, Alessandro, and Wil van der Aalst. "Extracting multiple viewpoint models from relational databases." Data-Driven Process Discovery and Analysis. Springer, Cham, 2018. 24-51.

    :param ocel: object-centric event log
    :param business_hours: boolean value that enables the usage of the business hours
    :param worktiming: (if business hours are in use) work timing during the day (default: [7, 17])
    :param weekends: (if business hours are in use) weekends (default: [6, 7])
    :rtype: ``Dict[str, Any]``
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
    """
    from pm4py.algo.discovery.ocel.ocpn import algorithm as ocpn_discovery
    return ocpn_discovery.apply(ocel)
