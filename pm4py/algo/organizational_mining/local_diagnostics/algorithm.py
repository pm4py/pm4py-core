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
from typing import Union, Optional, Dict, Any, List

import pandas as pd

from pm4py.algo.organizational_mining import util
from pm4py.objects.log.obj import EventLog
from pm4py.util import constants


class Parameters(Enum):
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    GROUP_KEY = constants.PARAMETER_CONSTANT_GROUP_KEY


class Outputs(Enum):
    GROUP_RELATIVE_FOCUS = "group_relative_focus"
    GROUP_RELATIVE_STAKE = "group_relative_stake"
    GROUP_COVERAGE = "group_coverage"
    GROUP_MEMBER_CONTRIBUTION = "group_member_contribution"


def apply_from_clustering_or_roles(log_obj: Union[pd.DataFrame, EventLog], ja_clustering_or_roles: Dict[str, List[str]],
                                   parameters: Optional[Dict[Any, str]] = None) -> Dict[str, Any]:
    """
    Provides the local diagnostics for the organizational model starting from a log object and the results
    of the similar activities clustering / the roles detection algorithm.

    The approach implemented is the one described in:
    Yang, Jing, et al. "OrgMining 2.0: A Novel Framework for Organizational Model Mining from Event Logs."
    arXiv preprint arXiv:2011.12445 (2020).

    Parameters
    --------------
    log_obj
        Log object
    ja_clustering_or_roles
        Result of the similar activities clustering / the roles detection algorithm
    parameters
        Parameters of the algorithm, including:
        - pm4py:param:resource_key => the resource attribute
        - pm4py:param:activity_key => the activity attribute
        - pm4py:param:group_key => the group

    Returns
    ---------------
    Dictionary containing four keys:
        - group_relative_focus => relative focus metric
        - group_relative_stake => relative stake metric
        - group_coverage => group coverage metric
        - group_member_contribution => group member contribution metric
    """
    if parameters is None:
        parameters = {}

    res_act, act_res = util.get_res_act_from_log(log_obj, parameters=parameters)
    resources = util.get_resources_from_log(log_obj, parameters=parameters)

    if type(ja_clustering_or_roles) is list:
        ja_clustering_or_roles = {str(i): ja_clustering_or_roles[i].originator_importance for i in range(len(ja_clustering_or_roles))}

    groups = {}
    for cluster in ja_clustering_or_roles:
        groups[cluster] = {}
        for res in ja_clustering_or_roles[cluster]:
            groups[cluster][res] = resources[res]

    return __apply(res_act, act_res, groups, parameters=parameters)


def apply_from_group_attribute(log_obj: Union[pd.DataFrame, EventLog], parameters: Optional[Dict[Any, str]] = None) -> Dict[str, Any]:
    """
    Provides the local diagnostics for the organizational model starting from a log object and considering
    the group specified by the attribute

    The approach implemented is the one described in:
    Yang, Jing, et al. "OrgMining 2.0: A Novel Framework for Organizational Model Mining from Event Logs."
    arXiv preprint arXiv:2011.12445 (2020).

    Parameters
    --------------
    log_obj
        Log object
    parameters
        Parameters of the algorithm, including:
        - pm4py:param:resource_key => the resource attribute
        - pm4py:param:activity_key => the activity attribute
        - pm4py:param:group_key => the group

    Returns
    ---------------
    Dictionary containing four keys:
        - group_relative_focus => relative focus metric
        - group_relative_stake => relative stake metric
        - group_coverage => group coverage metric
        - group_member_contribution => group member contribution metric
    """
    if parameters is None:
        parameters = {}

    res_act, act_res = util.get_res_act_from_log(log_obj, parameters=parameters)
    groups = util.get_groups_from_log(log_obj, parameters=parameters)
    return __apply(res_act, act_res, groups, parameters=parameters)


def __apply(res_act: Dict[str, Dict[str, int]], act_res: Dict[str, Dict[str, int]], groups: Dict[str, Dict[str, int]],
            parameters: Optional[Dict[Any, str]] = None) -> Dict[str, Any]:
    """
    Provides the local diagnostics for the organizational model

    The approach implemented is the one described in:
    Yang, Jing, et al. "OrgMining 2.0: A Novel Framework for Organizational Model Mining from Event Logs."
    arXiv preprint arXiv:2011.12445 (2020).

    Parameters
    ----------------
    res_act
        Dictionary resources-activities-occurrences
    act_res
        Dictionary activities-resources-occurrences
    groups
        Dictionary groups-resources-occurrences
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    dict
        Dictionary containing four keys:
        - group_relative_focus => relative focus metric
        - group_relative_stake => relative stake metric
        - group_coverage => group coverage metric
        - group_member_contribution => group member contribution metric
    """
    if parameters is None:
        parameters = {}

    ret = {}
    ret[Outputs.GROUP_RELATIVE_FOCUS.value] = __group_relative_focus(res_act, act_res, groups, parameters=parameters)
    ret[Outputs.GROUP_RELATIVE_STAKE.value] = __group_relative_stake(res_act, act_res, groups, parameters=parameters)
    ret[Outputs.GROUP_COVERAGE.value] = __group_coverage(res_act, act_res, groups, parameters=parameters)
    ret[Outputs.GROUP_MEMBER_CONTRIBUTION.value] = __group_member_contribution(res_act, act_res, groups,
                                                                               parameters=parameters)

    return ret


def __group_relative_focus(res_act: Dict[str, Dict[str, int]], act_res: Dict[str, Dict[str, int]],
                           groups: Dict[str, Dict[str, int]], parameters: Optional[Dict[Any, str]] = None) -> Dict[
    str, Dict[str, float]]:
    """
    Calculates the relative focus metric

    GROUP RELATIVE FOCUS (on a given type of work) specifies how much a resource group performed this type of work
    compared to the overall workload of the group. It can be used to measure how the workload of a resource group
    is distributed over different types of work, i.e., work diversification of the group.

    The approach implemented is the one described in:
    Yang, Jing, et al. "OrgMining 2.0: A Novel Framework for Organizational Model Mining from Event Logs."
    arXiv preprint arXiv:2011.12445 (2020).

    Parameters
    ----------------
    res_act
        Dictionary resources-activities-occurrences
    act_res
        Dictionary activities-resources-occurrences
    groups
        Dictionary groups-resources-occurrences
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    metric
        Metric value
    """
    ret = {}
    for g in groups:
        res_in_g = groups[g]
        ret[g] = {}
        for a in act_res:
            this = 0
            total = 0
            for r in act_res[a]:
                total += act_res[a][r]
                if r in res_in_g:
                    this += act_res[a][r]
            ret[g][a] = float(this) / float(total)
    return ret


def __group_relative_stake(res_act: Dict[str, Dict[str, int]], act_res: Dict[str, Dict[str, int]],
                           groups: Dict[str, Dict[str, int]], parameters: Optional[Dict[Any, str]] = None) -> Dict[
    str, Dict[str, float]]:
    """
    Calculates the relative stake metric

    GROUP RELATIVE STAKE (in a given type of work) specifies how much this type of work was performed by a certain
    resource group among all groups. It can be used to measure how the workload devoted to a certain type of work is
    distributed over resource groups in an organizational model, i.e., work participation by different groups.

    The approach implemented is the one described in:
    Yang, Jing, et al. "OrgMining 2.0: A Novel Framework for Organizational Model Mining from Event Logs."
    arXiv preprint arXiv:2011.12445 (2020).

    Parameters
    ----------------
    res_act
        Dictionary resources-activities-occurrences
    act_res
        Dictionary activities-resources-occurrences
    groups
        Dictionary groups-resources-occurrences
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    metric
        Metric value
    """
    ret = {}
    for g in groups:
        total = 0
        res_in_g = groups[g]
        ret[g] = {}
        for a in act_res:
            this = 0
            for r in act_res[a]:
                if r in res_in_g:
                    total += act_res[a][r]
                    this += act_res[a][r]
            ret[g][a] = this
        for a in act_res:
            ret[g][a] = float(ret[g][a]) / float(total)
    return ret


def __group_coverage(res_act: Dict[str, Dict[str, int]], act_res: Dict[str, Dict[str, int]],
                     groups: Dict[str, Dict[str, int]], parameters: Optional[Dict[Any, str]] = None) -> Dict[
    str, Dict[str, float]]:
    """
    Calculates the group coverage metric

    GROUP COVERAGE with respect to a given type of work specifies the proportion of members of a resource group that
    performed this type of work.

    The approach implemented is the one described in:
    Yang, Jing, et al. "OrgMining 2.0: A Novel Framework for Organizational Model Mining from Event Logs."
    arXiv preprint arXiv:2011.12445 (2020).

    Parameters
    ----------------
    res_act
        Dictionary resources-activities-occurrences
    act_res
        Dictionary activities-resources-occurrences
    groups
        Dictionary groups-resources-occurrences
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    metric
        Metric value
    """
    ret = {}
    for g in groups:
        ret[g] = {}
        total = sum(groups[g].values())
        for r in groups[g]:
            ret[g][r] = float(groups[g][r]) / float(total)
    return ret


def __group_member_contribution(res_act: Dict[str, Dict[str, int]], act_res: Dict[str, Dict[str, int]],
                                groups: Dict[str, Dict[str, int]], parameters: Optional[Dict[Any, str]] = None) -> Dict[
    str, Dict[str, Dict[str, int]]]:
    """
    Calculates the member contribution metric

    GROUP MEMBER CONTRIBUTION of a member of a resource group with respect to the given type of work specifies how
    much of this type of work by the group was performed by the member. It can be used to measure how the workload
    of the entire group devoted to a certain type of work is distributed over the group members.

    The approach implemented is the one described in:
    Yang, Jing, et al. "OrgMining 2.0: A Novel Framework for Organizational Model Mining from Event Logs."
    arXiv preprint arXiv:2011.12445 (2020).

    Parameters
    ----------------
    res_act
        Dictionary resources-activities-occurrences
    act_res
        Dictionary activities-resources-occurrences
    groups
        Dictionary groups-resources-occurrences
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    metric
        Metric value
    """
    ret = {}
    for g in groups:
        ret[g] = {}
        for r in groups[g]:
            ret[g][r] = res_act[r]
    return ret
