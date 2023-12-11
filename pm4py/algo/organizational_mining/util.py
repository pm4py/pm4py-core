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
from typing import Union, Optional, Dict, Any, Tuple

import pandas as pd

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventLog
from pm4py.util import xes_constants, constants, exec_utils, pandas_utils


class Parameters(Enum):
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    GROUP_KEY = constants.PARAMETER_CONSTANT_GROUP_KEY


def get_groups_from_log(log_obj: Union[pd.DataFrame, EventLog], parameters: Optional[Dict[Any, str]] = None) -> Dict[
    str, Dict[str, int]]:
    """
    From the log object, where events have a group, a resource and an activity attribute,
    gets a dictionary where the first key is a group, the second key is a resource and the value is the number
    of events done by the resource when belonging to the given group.

    Parameters
    ---------------
    log_obj
        Log object
    parameters
        Parameters of the algorithm, including:
        - Parameters.RESOURCE_KEY => the resource attribute
        - Parameters.ACTIVITY_KEY => the activity attribute
        - Parameters.GROUP_KEY => the group

    Returns
    ---------------
    dict
        Aforementioned dictionary
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)
    group_key = exec_utils.get_param_value(Parameters.GROUP_KEY, parameters, xes_constants.DEFAULT_GROUP_KEY)

    groups = {}

    if pandas_utils.check_is_pandas_dataframe(log_obj):
        group_res = log_obj.groupby([resource_key, group_key]).count().to_dict()[activity_key]
        for el in group_res:
            if not el[1] in groups:
                groups[el[1]] = {}
            groups[el[1]][el[0]] = group_res[el]
    else:
        log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
        for trace in log_obj:
            for event in trace:
                if activity_key in event and resource_key in event and group_key in event:
                    group = event[group_key]
                    resource = event[resource_key]
                    if group not in groups:
                        groups[group] = {}
                    if resource not in groups[group]:
                        groups[group][resource] = 0
                    groups[group][resource] += 1

    return groups


def get_res_act_from_log(log_obj: Union[pd.DataFrame, EventLog], parameters: Optional[Dict[Any, str]] = None) -> Tuple[
    Dict[str, Dict[str, int]], Dict[str, Dict[str, int]]]:
    """
    From the log object, where events have a group, a resource and an activity attribute,
    gets two dictionaries:
    - The first, where the first key is the resource, the second key is the activity and the third is the number of
        events of the given activity done by the given resource
    - The second, where the first key is the activity, the second key is the resource and the third is the number of
        events of the given activity done by the given resource

    Parameters
    ---------------
    log_obj
        Log object
    parameters
        Parameters of the algorithm, including:
        - Parameters.RESOURCE_KEY => the resource attribute
        - Parameters.ACTIVITY_KEY => the activity attribute
        - Parameters.GROUP_KEY => the group

    Returns
    ---------------
    res_act
        Dictionary resources-activities-occurrences
    act_res
        Dictionary activities-resources-occurrences
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)
    group_key = exec_utils.get_param_value(Parameters.GROUP_KEY, parameters, xes_constants.DEFAULT_GROUP_KEY)

    res_act = {}
    act_res = {}

    if pandas_utils.check_is_pandas_dataframe(log_obj):
        aggr = log_obj.groupby([activity_key, resource_key]).count().to_dict()[group_key]
        for el in aggr:
            if not el[1] in res_act:
                res_act[el[1]] = {}
            if not el[0] in act_res:
                act_res[el[0]] = {}
            res_act[el[1]][el[0]] = aggr[el]
            act_res[el[0]][el[1]] = aggr[el]
    else:
        log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
        for trace in log_obj:
            for event in trace:
                if activity_key in event and resource_key in event:
                    activity = event[activity_key]
                    resource = event[resource_key]
                    if resource not in res_act:
                        res_act[resource] = {}
                    if activity not in act_res:
                        act_res[activity] = {}
                    if activity not in res_act[resource]:
                        res_act[resource][activity] = 0
                    if resource not in act_res[activity]:
                        act_res[activity][resource] = 0
                    res_act[resource][activity] += 1
                    act_res[activity][resource] += 1

    return res_act, act_res


def get_resources_from_log(log_obj: Union[pd.DataFrame, EventLog], parameters: Optional[Dict[Any, str]] = None) -> Dict[
    str, int]:
    """
    Gets the resources, along with the respective number of events, from the log object

    Parameters
    ----------------
    log_obj
        Log object
    parameters
        Parameters of the algorithm, including:
        - Parameters.RESOURCE_KEY => the resource attribute
        - Parameters.ACTIVITY_KEY => the activity attribute
        - Parameters.GROUP_KEY => the group

    Returns
    ----------------
    resources_dictionary
        Dictionary of resources along with their occurrences
    """
    if parameters is None:
        parameters = {}

    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)

    resources = {}

    if pandas_utils.check_is_pandas_dataframe(log_obj):
        resources = log_obj[resource_key].value_counts().to_dict()
    else:
        for trace in log_obj:
            for event in trace:
                resource = event[resource_key]
                if resource not in resources:
                    resources[resource] = 0
                resources[resource] += 1

    return resources
