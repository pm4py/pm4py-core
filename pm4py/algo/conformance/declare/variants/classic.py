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
from pm4py.objects.log.obj import EventLog
import pandas as pd
from typing import Union, Dict, Optional, Any, List
from pm4py.algo.discovery.declare.templates import *
from pm4py.util import exec_utils, constants, xes_constants
from collections import Counter


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def __check_existence(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]], trace_dict: Dict[str, List[Any]],
                      parameters: Optional[Dict[Any, Any]] = None):
    if EXISTENCE in model:
        for act in model[EXISTENCE]:
            if act not in trace:
                trace_dict["deviations"].append([EXISTENCE, act])


def __check_absence(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]], trace_dict: Dict[str, List[Any]],
                    parameters: Optional[Dict[Any, Any]] = None):
    if ABSENCE in model:
        for act in model[ABSENCE]:
            if act in trace:
                trace_dict["deviations"].append([ABSENCE, act])


def __check_exactly_one(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]], trace_dict: Dict[str, List[Any]],
                        parameters: Optional[Dict[Any, Any]] = None):
    if EXACTLY_ONE in model:
        trace_counter = Counter(trace)
        for act in model[EXACTLY_ONE]:
            if trace_counter[act] != 1:
                trace_dict["deviations"].append([EXACTLY_ONE, act])


def __check_init(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]], trace_dict: Dict[str, List[Any]],
                 parameters: Optional[Dict[Any, Any]] = None):
    if INIT in model:
        for act in model[INIT]:
            if len(trace) == 0 or trace[0] != act:
                trace_dict["deviations"].append([INIT, act])


def __check_responded_existence(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]],
                                trace_dict: Dict[str, List[Any]], parameters: Optional[Dict[Any, Any]] = None):
    if RESPONDED_EXISTENCE in model:
        for act_couple in model[RESPONDED_EXISTENCE]:
            if act_couple[0] in trace and act_couple[1] not in trace:
                trace_dict["deviations"].append([RESPONDED_EXISTENCE, act_couple])


def __check_coexistence(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]], trace_dict: Dict[str, List[Any]],
                        parameters: Optional[Dict[Any, Any]] = None):
    if COEXISTENCE in model:
        for act_couple in model[COEXISTENCE]:
            if (act_couple[0] in trace and act_couple[1] not in trace) or (
                    act_couple[1] in trace and act_couple[0] not in trace):
                trace_dict["deviations"].append([COEXISTENCE, act_couple])


def __check_non_coexistence(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]],
                            trace_dict: Dict[str, List[Any]], parameters: Optional[Dict[Any, Any]] = None):
    if NONCOEXISTENCE in model:
        for act_couple in model[NONCOEXISTENCE]:
            if act_couple[0] in trace and act_couple[1] in trace:
                trace_dict["deviations"].append([NONCOEXISTENCE, act_couple])


def __check_response(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]], trace_dict: Dict[str, List[Any]],
                     act_idxs: Dict[str, List[int]], parameters: Optional[Dict[Any, Any]] = None):
    if RESPONSE in model:
        for act_couple in model[RESPONSE]:
            if act_couple[0] in trace:
                if (not act_couple[1] in trace) or max(act_idxs[act_couple[0]]) > max(act_idxs[act_couple[1]]):
                    trace_dict["deviations"].append([RESPONSE, act_couple])


def __check_precedence(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]], trace_dict: Dict[str, List[Any]],
                       act_idxs: Dict[str, List[int]], parameters: Optional[Dict[Any, Any]] = None):
    if PRECEDENCE in model:
        for act_couple in model[PRECEDENCE]:
            if act_couple[1] in trace:
                if (not act_couple[0] in trace) or min(act_idxs[act_couple[0]]) > min(act_idxs[act_couple[1]]):
                    trace_dict["deviations"].append([PRECEDENCE, act_couple])


def __check_succession(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]], trace_dict: Dict[str, List[Any]],
                       act_idxs: Dict[str, List[int]], parameters: Optional[Dict[Any, Any]] = None):
    if SUCCESSION in model:
        for act_couple in model[SUCCESSION]:
            if (not act_couple[0] in trace or not act_couple[1] in trace) or min(act_idxs[act_couple[0]]) > min(
                    act_idxs[act_couple[1]]) or max(act_idxs[act_couple[0]]) > max(act_idxs[act_couple[1]]):
                trace_dict["deviations"].append([SUCCESSION, act_couple])


def __check_alt_response(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]],
                         trace_dict: Dict[str, List[Any]], act_idxs: Dict[str, List[int]],
                         parameters: Optional[Dict[Any, Any]] = None):
    if ALTRESPONSE in model:
        for act_couple in model[RESPONSE]:
            spec_idxs = []
            if act_couple[0] in trace:
                spec_idxs = spec_idxs + [(act_couple[0], i) for i in act_idxs[act_couple[0]]]
            if act_couple[1] in trace:
                spec_idxs = spec_idxs + [(act_couple[1], i) for i in act_idxs[act_couple[1]]]
            spec_idxs = sorted(spec_idxs, key=lambda x: (x[1], x[0]))
            while spec_idxs:
                if spec_idxs[0][0] != act_couple[0]:
                    del spec_idxs[0]
                else:
                    break
            is_ok = True
            for i in range(len(spec_idxs)):
                if i % 2 == 0 and (spec_idxs[i][0] != act_couple[0] or i == len(spec_idxs) - 1 or spec_idxs[i + 1][0] !=
                                   act_couple[1]):
                    is_ok = False
                    break
            if not is_ok:
                trace_dict["deviations"].append([ALTRESPONSE, act_couple])


def __check_chain_response(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]],
                           trace_dict: Dict[str, List[Any]], act_idxs: Dict[str, List[int]],
                           parameters: Optional[Dict[Any, Any]] = None):
    if CHAINRESPONSE in model:
        for act_couple in model[CHAINRESPONSE]:
            spec_idxs = []
            if act_couple[0] in trace:
                spec_idxs = spec_idxs + [(act_couple[0], i) for i in act_idxs[act_couple[0]]]
            if act_couple[1] in trace:
                spec_idxs = spec_idxs + [(act_couple[1], i) for i in act_idxs[act_couple[1]]]
            spec_idxs = sorted(spec_idxs, key=lambda x: (x[1], x[0]))
            while spec_idxs:
                if spec_idxs[0][0] != act_couple[0]:
                    del spec_idxs[0]
                else:
                    break
            is_ok = True
            for i in range(len(spec_idxs)):
                if i % 2 == 0 and (spec_idxs[i][0] != act_couple[0] or i == len(spec_idxs) - 1 or spec_idxs[i + 1][0] !=
                                   act_couple[1] or spec_idxs[i + 1][1] != spec_idxs[i][1] + 1):
                    is_ok = False
                    break
            if not is_ok:
                trace_dict["deviations"].append([CHAINRESPONSE, act_couple])


def __check_alt_precedence(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]],
                           trace_dict: Dict[str, List[Any]], act_idxs: Dict[str, List[int]],
                           parameters: Optional[Dict[Any, Any]] = None):
    if ALTPRECEDENCE in model:
        for act_couple in model[ALTPRECEDENCE]:
            spec_idxs = []
            if act_couple[0] in trace:
                spec_idxs = spec_idxs + [(act_couple[0], i) for i in act_idxs[act_couple[0]]]
            if act_couple[1] in trace:
                spec_idxs = spec_idxs + [(act_couple[1], i) for i in act_idxs[act_couple[1]]]
            spec_idxs = sorted(spec_idxs, key=lambda x: (x[1], x[0]))
            while len(spec_idxs) > 1:
                if spec_idxs[1][0] != act_couple[1]:
                    del spec_idxs[0]
                else:
                    break
            is_ok = True
            for i in range(len(spec_idxs)):
                if i % 2 == 0 and (spec_idxs[i][0] != act_couple[0] or i == len(spec_idxs) - 1 or spec_idxs[i + 1][0] !=
                                   act_couple[1]):
                    is_ok = False
                    break
            if not is_ok:
                trace_dict["deviations"].append([ALTPRECEDENCE, act_couple])


def __check_chain_precedence(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]],
                             trace_dict: Dict[str, List[Any]], act_idxs: Dict[str, List[int]],
                             parameters: Optional[Dict[Any, Any]] = None):
    if CHAINPRECEDENCE in model:
        for act_couple in model[CHAINPRECEDENCE]:
            spec_idxs = []
            if act_couple[0] in trace:
                spec_idxs = spec_idxs + [(act_couple[0], i) for i in act_idxs[act_couple[0]]]
            if act_couple[1] in trace:
                spec_idxs = spec_idxs + [(act_couple[1], i) for i in act_idxs[act_couple[1]]]
            spec_idxs = sorted(spec_idxs, key=lambda x: (x[1], x[0]))
            while len(spec_idxs) > 1:
                if spec_idxs[1][0] != act_couple[1]:
                    del spec_idxs[0]
                else:
                    break
            is_ok = True
            for i in range(len(spec_idxs)):
                if i % 2 == 0 and (spec_idxs[i][0] != act_couple[0] or i == len(spec_idxs) - 1 or spec_idxs[i + 1][0] !=
                                   act_couple[1] or spec_idxs[i + 1][1] != spec_idxs[i][1] + 1):
                    is_ok = False
                    break
            if not is_ok:
                trace_dict["deviations"].append([CHAINPRECEDENCE, act_couple])


def __check_alt_succession(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]],
                           trace_dict: Dict[str, List[Any]], act_idxs: Dict[str, List[int]],
                           parameters: Optional[Dict[Any, Any]] = None):
    if ALTSUCCESSION in model:
        for act_couple in model[ALTSUCCESSION]:
            spec_idxs = []
            if act_couple[0] in trace:
                spec_idxs = spec_idxs + [(act_couple[0], i) for i in act_idxs[act_couple[0]]]
            if act_couple[1] in trace:
                spec_idxs = spec_idxs + [(act_couple[1], i) for i in act_idxs[act_couple[1]]]
            spec_idxs = sorted(spec_idxs, key=lambda x: (x[1], x[0]))
            is_ok = True
            for i in range(len(spec_idxs)):
                if i % 2 == 0 and (spec_idxs[i][0] != act_couple[0] or i == len(spec_idxs) - 1 or spec_idxs[i + 1][0] !=
                                   act_couple[1]):
                    is_ok = False
                    break
            if not is_ok:
                trace_dict["deviations"].append([ALTSUCCESSION, act_couple])


def __check_chain_succession(trace: List[str], model: Dict[str, Dict[Any, Dict[str, int]]],
                             trace_dict: Dict[str, List[Any]], act_idxs: Dict[str, List[int]],
                             parameters: Optional[Dict[Any, Any]] = None):
    if CHAINSUCCESSION in model:
        for act_couple in model[CHAINSUCCESSION]:
            spec_idxs = []
            if act_couple[0] in trace:
                spec_idxs = spec_idxs + [(act_couple[0], i) for i in act_idxs[act_couple[0]]]
            if act_couple[1] in trace:
                spec_idxs = spec_idxs + [(act_couple[1], i) for i in act_idxs[act_couple[1]]]
            spec_idxs = sorted(spec_idxs, key=lambda x: (x[1], x[0]))
            is_ok = True
            for i in range(len(spec_idxs)):
                if i % 2 == 0 and (spec_idxs[i][0] != act_couple[0] or i == len(spec_idxs) - 1 or spec_idxs[i + 1][0] !=
                                   act_couple[1] or spec_idxs[i + 1][1] != spec_idxs[i][1] + 1):
                    is_ok = False
                    break
            if not is_ok:
                trace_dict["deviations"].append([CHAINSUCCESSION, act_couple])


def apply_list(projected_log: List[List[str]], model: Dict[str, Dict[Any, Dict[str, int]]],
               parameters: Optional[Dict[Any, Any]] = None) -> List[Dict[str, Any]]:
    if parameters is None:
        parameters = {}

    conf_cases = []

    total_num_constraints = 0
    for k in model:
        total_num_constraints += len(model[k])

    for trace in projected_log:
        act_idxs = {}
        for i in range(len(trace)):
            if trace[i] not in act_idxs:
                act_idxs[trace[i]] = []
            act_idxs[trace[i]].append(i)

        ret = {}
        ret["no_constr_total"] = total_num_constraints
        ret["deviations"] = []

        __check_existence(trace, model, ret, parameters)
        __check_exactly_one(trace, model, ret, parameters)
        __check_init(trace, model, ret, parameters)
        __check_responded_existence(trace, model, ret, parameters)
        __check_coexistence(trace, model, ret, parameters)
        __check_non_coexistence(trace, model, ret, parameters)
        __check_response(trace, model, ret, act_idxs, parameters)
        __check_precedence(trace, model, ret, act_idxs, parameters)
        __check_succession(trace, model, ret, act_idxs, parameters)
        __check_alt_response(trace, model, ret, act_idxs, parameters)
        __check_chain_response(trace, model, ret, act_idxs, parameters)
        __check_alt_precedence(trace, model, ret, act_idxs, parameters)
        __check_chain_precedence(trace, model, ret, act_idxs, parameters)
        __check_alt_succession(trace, model, ret, act_idxs, parameters)
        __check_chain_succession(trace, model, ret, act_idxs, parameters)
        __check_absence(trace, model, ret, parameters)
        __check_non_coexistence(trace, model, ret, parameters)

        ret["no_dev_total"] = len(ret["deviations"])
        ret["dev_fitness"] = 1 - ret["no_dev_total"] / ret["no_constr_total"]
        ret["is_fit"] = ret["no_dev_total"] == 0

        conf_cases.append(ret)

    return conf_cases


def apply(log: Union[EventLog, pd.DataFrame], model: Dict[str, Dict[Any, Dict[str, int]]],
          parameters: Optional[Dict[Any, Any]] = None) -> List[Dict[str, Any]]:
    """
    Applies conformance checking against a DECLARE model.

    Paper:
    F. M. Maggi, A. J. Mooij and W. M. P. van der Aalst, "User-guided discovery of declarative process models," 2011 IEEE Symposium on Computational Intelligence and Data Mining (CIDM), Paris, France, 2011, pp. 192-199, doi: 10.1109/CIDM.2011.5949297.

    Parameters
    --------------
    log
        Event log / Pandas dataframe
    model
        DECLARE model
    parameters
        Possible parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity
        - Parameters.CASE_ID_KEY => the attribute to be used as case identifier

    Returns
    -------------
    lst_conf_res
        List containing for every case a dictionary with different keys:
        - no_constr_total => the total number of constraints of the DECLARE model
        - deviations => a list of deviations
        - no_dev_total => the total number of deviations
        - dev_fitness => the fitness (1 - no_dev_total / no_constr_total)
        - is_fit => True if the case is perfectly fit
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)

    import pm4py

    projected_log = pm4py.project_on_event_attribute(log, activity_key, case_id_key=case_id_key)

    ret = apply_list(projected_log, model, parameters=parameters)

    return ret


def get_diagnostics_dataframe(log, conf_result, parameters=None) -> pd.DataFrame:
    """
    Gets the diagnostics dataframe from a log and the results
    of DECLARE-based conformance checking

    Parameters
    --------------
    log
        Event log
    conf_result
        Results of conformance checking

    Returns
    --------------
    diagn_dataframe
        Diagnostics dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)

    import pandas as pd

    diagn_stream = []

    for index in range(len(log)):
        case_id = log[index].attributes[case_id_key]

        no_dev_total = conf_result[index]["no_dev_total"]
        no_constr_total = conf_result[index]["no_constr_total"]
        dev_fitness = conf_result[index]["dev_fitness"]

        diagn_stream.append({"case_id": case_id, "no_dev_total": no_dev_total, "no_constr_total": no_constr_total,
                             "dev_fitness": dev_fitness})

    return pd.DataFrame(diagn_stream)
