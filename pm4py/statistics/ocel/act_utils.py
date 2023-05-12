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
from typing import Optional, Dict, Any, Tuple, Set
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel import constants as ocel_constants
import pandas as pd
from pm4py.objects.ocel.obj import OCEL
from copy import copy


class Parameters(Enum):
    EVENT_ID = ocel_constants.PARAM_EVENT_ID
    OBJECT_ID = ocel_constants.PARAM_OBJECT_ID
    EVENT_ACTIVITY = ocel_constants.PARAM_EVENT_ACTIVITY
    PREFILTERING = "prefiltering"


def aggregate_events(associations: Dict[str, Set[Tuple[str, str]]]) -> Dict[str, Set[str]]:
    """
    Utility method to calculate the "events" metric from the associations.
    """
    ret = {}
    for act in associations:
        ret[act] = set()
        for el in associations[act]:
            ret[act].add(el[0])
    return ret


def aggregate_unique_objects(associations: Dict[str, Set[Tuple[str, str]]]) -> Dict[str, Set[str]]:
    """
    Utility method to calculate the "unique objects" metric from the associations.
    """
    ret = {}
    for act in associations:
        ret[act] = set()
        for el in associations[act]:
            ret[act].add(el[1])
    return ret


def aggregate_total_objects(associations: Dict[str, Set[Tuple[str, str]]]) -> Dict[str, Set[Tuple[str, str]]]:
    """
    Utility method to calculate the "total objects" metric from the associations.
    """
    return associations


def find_associations_from_relations_df(relations_df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> \
Dict[
    str, Set[Tuple[str, str]]]:
    """
    Associates each activity in the relationship dataframe with the combinations
    of event identifiers and objects that are associated to the activity.

    Parameters
    ------------------
    rel_df
        Relations dataframe
    parameters
        Parameters of the method, including:
        - Parameters.EVENT_ID => the attribute to use as event identifier
        - Parameters.OBJECT_ID => the attribute to use as object identifier
        - Parameters.EVENT_ACTIVITY => the attribute to use as activity

    Returns
    -----------------
    dict_associations
        Dictionary that associates each activity to its (ev. id, obj id.) combinations.
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel_constants.DEFAULT_EVENT_ID)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel_constants.DEFAULT_OBJECT_ID)
    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters,
                                                ocel_constants.DEFAULT_EVENT_ACTIVITY)
    prefiltering = exec_utils.get_param_value(Parameters.PREFILTERING, parameters, "none")

    if prefiltering == "start":
        relations_df = relations_df.groupby(object_id).first().reset_index()
    elif prefiltering == "end":
        relations_df = relations_df.groupby(object_id).last().reset_index()

    ids = list(relations_df[event_id])
    oids = list(relations_df[object_id])
    acts = list(relations_df[event_activity])

    associations = {}

    i = 0
    while i < len(acts):
        if acts[i] not in associations:
            associations[acts[i]] = set()
        associations[acts[i]].add((ids[i], oids[i]))
        i = i + 1

    return associations


def find_associations_from_ocel(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Set[Any]]:
    """
    Associates each activity in the OCEL with the combinations
    of event identifiers and objects that are associated to the activity.

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
        Dictionary that associates each activity to its (ev. id, obj id.) combinations.
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel.object_id_column)
    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters,
                                                ocel.event_activity)

    new_parameters = copy(parameters)
    new_parameters[Parameters.EVENT_ID] = event_id
    new_parameters[Parameters.OBJECT_ID] = object_id
    new_parameters[Parameters.EVENT_ACTIVITY] = event_activity

    return find_associations_from_relations_df(ocel.relations, parameters=new_parameters)
