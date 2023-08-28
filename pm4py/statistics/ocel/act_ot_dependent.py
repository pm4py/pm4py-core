from typing import Optional, Dict, Any, Tuple, Set, List
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel import constants as ocel_constants
from pm4py.objects.ocel.obj import OCEL
from pm4py.statistics.ocel.act_utils import find_associations_from_relations_df


class Parameters(Enum):
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE


def aggregate_events(associations: Dict[str, Dict[str, Set[Tuple[str, str]]]]) -> Dict[
    str, Dict[str, Set[Tuple[str, str]]]]:
    """
    Utility method to calculate the "events" metric from the object-type specific associations.
    """
    ret = {}

    for ot in associations:
        ret[ot] = {}
        for act in associations[ot]:
            ret[ot][act] = set()
            for el in associations[ot][act]:
                ret[ot][act].add(el[0])

    return ret


def aggregate_unique_objects(associations: Dict[str, Dict[str, Set[Tuple[str, str]]]]) -> Dict[
    str, Dict[str, Set[Tuple[str, str]]]]:
    """
    Utility method to calculate the "unique objects" metric from the object-type specific associations.
    """
    ret = {}

    for ot in associations:
        ret[ot] = {}
        for act in associations[ot]:
            ret[ot][act] = set()
            for el in associations[ot][act]:
                ret[ot][act].add(el[1])

    return ret


def aggregate_total_objects(associations: Dict[str, Dict[str, Set[Tuple[str, str]]]]) -> Dict[
    str, Dict[str, Set[Tuple[str, str]]]]:
    """
    Utility method to calculate the "total objects" metric from the object-type specific associations.
    """
    return associations


def find_associations_from_ocel(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[
    str, Dict[str, List[Tuple[str, str]]]]:
    """
    Associates each object type and activity in the object-centric event log with the combinations
    of event identifiers and objects that are associated to them.

    Parameters
    ------------------
    ocel
        Object-centric event log
    parameters
        Parameters of the method, including:
        - Parameters.EVENT_ID => the attribute to use as event identifier
        - Parameters.OBJECT_ID => the attribute to use as object identifier
        - Parameters.EVENT_ACTIVITY => the attribute to use as activity

    Returns
    -----------------
    dict_associations
        Dictionary that associates each object type (first key) and activity (second key)
        to its (ev. id, obj id.) combinations.
    """
    if parameters is None:
        parameters = {}

    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)

    ret = {}

    for ot, relations in ocel.relations.groupby(object_type):
        ret[ot] = find_associations_from_relations_df(relations, parameters=parameters)

    return ret
