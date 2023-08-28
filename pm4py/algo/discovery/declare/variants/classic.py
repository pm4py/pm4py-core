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
from pm4py.algo.discovery.declare.templates import *
import pandas as pd
from typing import Union, Dict, Optional, Any, Tuple, Collection, Set, List
from typing import Counter as TCounter
from pm4py.util import exec_utils, constants, xes_constants
from collections import Counter


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    CONSIDERED_ACTIVITIES = "considered_activities"
    MIN_SUPPORT_RATIO = "min_support_ratio"
    MIN_CONFIDENCE_RATIO = "min_confidence_ratio"
    AUTO_SELECTION_MULTIPLIER = "auto_selection_multiplier"
    ALLOWED_TEMPLATES = "allowed_templates"


def __rule_existence_column(act: str) -> Tuple[str, str]:
    return (EXISTENCE, act)


def __rule_exactly_one_column(act: str) -> Tuple[str, str]:
    return (EXACTLY_ONE, act)


def __rule_init_column(act: str) -> Tuple[str, str]:
    return (INIT, act)


def __rule_responded_existence_column(act: str, act2: str) -> Tuple[str, str, str]:
    return (RESPONDED_EXISTENCE, act, act2)


def __rule_response(act: str, act2: str) -> Tuple[str, str, str]:
    return (RESPONSE, act, act2)


def __rule_precedence(act: str, act2: str) -> Tuple[str, str, str]:
    return (PRECEDENCE, act, act2)


def __rule_succession(act: str, act2: str) -> Tuple[str, str, str]:
    return (SUCCESSION, act, act2)


def __rule_alternate_response(act: str, act2: str) -> Tuple[str, str, str]:
    return (ALTRESPONSE, act, act2)


def __rule_alternate_precedence(act: str, act2: str) -> Tuple[str, str, str]:
    return (ALTPRECEDENCE, act, act2)


def __rule_alternate_succession(act: str, act2: str) -> Tuple[str, str, str]:
    return (ALTSUCCESSION, act, act2)


def __rule_chain_response(act: str, act2: str) -> Tuple[str, str, str]:
    return (CHAINRESPONSE, act, act2)


def __rule_chain_precedence(act: str, act2: str) -> Tuple[str, str, str]:
    return (CHAINPRECEDENCE, act, act2)


def __rule_chain_succession(act: str, act2: str) -> Tuple[str, str, str]:
    return (CHAINSUCCESSION, act, act2)


def __rule_absence_act(act: str) -> Tuple[str, str]:
    return (ABSENCE, act)


def __rule_coexistence(act: str, act2: str) -> Tuple[str, str, str]:
    return (COEXISTENCE, act, act2)


def __rule_non_coexistence(act: str, act2: str) -> Tuple[str, str, str]:
    return (NONCOEXISTENCE, act, act2)


def __rule_non_succession(act: str, act2: str) -> Tuple[str, str, str]:
    return (NONSUCCESSION, act, act2)


def __rule_non_chain_succession(act: str, act2: str) -> Tuple[str, str, str]:
    return (NONCHAINSUCCESSION, act, act2)


def __col_to_dict_rule(col_name: Union[Tuple[str, str], Tuple[str, str, str]]) -> Tuple[str, Any]:
    if len(col_name) == 2:
        return col_name[0], col_name[1]
    else:
        return col_name[0], (col_name[1], col_name[2])


def existence_template_step1(rules: Dict[Union[Tuple[str, str], Tuple[str, str, str]], int], trace: Collection[str],
                             activities: Set[str], act_counter: TCounter[str], act_idxs: Dict[str, List[int]],
                             allowed_templates: Collection[str]):
    if EXISTENCE in allowed_templates:
        for act in activities:
            if act in act_counter:
                rules[__rule_existence_column(act)] = 1
            else:
                rules[__rule_existence_column(act)] = -1


def exactly_one_template_step1(rules: Dict[Union[Tuple[str, str], Tuple[str, str, str]], int], trace: Collection[str],
                               activities: Set[str], act_counter: TCounter[str], act_idxs: Dict[str, List[int]],
                               allowed_templates: Collection[str]):
    if EXACTLY_ONE in allowed_templates:
        for act in activities:
            if act in act_counter:
                if act_counter[act] == 1:
                    rules[__rule_exactly_one_column(act)] = 1
                else:
                    rules[__rule_exactly_one_column(act)] = -1


def init_template_step1(rules: Dict[Union[Tuple[str, str], Tuple[str, str, str]], int], trace: Collection[str],
                        activities: Set[str], act_counter: TCounter[str], act_idxs: Dict[str, List[int]],
                        allowed_templates: Collection[str]):
    if INIT in allowed_templates:
        for act in activities:
            if act == trace[0]:
                rules[__rule_init_column(act)] = 1
            else:
                rules[__rule_init_column(act)] = -1


def responded_existence_template_step1(rules: Dict[Union[Tuple[str, str], Tuple[str, str, str]], int],
                                       trace: Collection[str], activities: Set[str], act_counter: TCounter[str],
                                       act_idxs: Dict[str, List[int]], allowed_templates: Collection[str]):
    if RESPONDED_EXISTENCE in allowed_templates:
        for act in act_counter:
            for act2 in activities:
                if act2 != act:
                    if act2 not in act_counter:
                        rules[__rule_responded_existence_column(act, act2)] = -1
                    else:
                        rules[__rule_responded_existence_column(act, act2)] = 1


def response_template_step1(rules: Dict[Union[Tuple[str, str], Tuple[str, str, str]], int], trace: Collection[str],
                            activities: Set[str], act_counter: TCounter[str], act_idxs: Dict[str, List[int]],
                            allowed_templates: Collection[str]):
    if RESPONSE in allowed_templates:
        for act in act_counter:
            for act2 in activities:
                if act2 != act:
                    if act2 not in act_counter:
                        rules[__rule_response(act, act2)] = -1
                    else:
                        if act_idxs[act][-1] < act_idxs[act2][-1]:
                            rules[__rule_response(act, act2)] = 1
                        else:
                            rules[__rule_response(act, act2)] = -1


def precedence_template_step1(rules: Dict[Union[Tuple[str, str], Tuple[str, str, str]], int], trace: Collection[str],
                              activities: Set[str], act_counter: TCounter[str], act_idxs: Dict[str, List[int]],
                              allowed_templates: Collection[str]):
    if PRECEDENCE in allowed_templates:
        for act in act_counter:
            for act2 in activities:
                if act2 != act:
                    if act2 not in act_counter:
                        pass
                    else:
                        if act_idxs[act2][0] < act_idxs[act][0]:
                            rules[__rule_precedence(act2, act)] = 1
                        else:
                            rules[__rule_precedence(act2, act)] = -1


def altresponse_template_step1(rules: Dict[Union[Tuple[str, str], Tuple[str, str, str]], int], trace: Collection[str],
                               activities: Set[str], act_counter: TCounter[str], act_idxs: Dict[str, List[int]],
                               allowed_templates: Collection[str]):
    if ALTRESPONSE in allowed_templates:
        for act in act_counter:
            for act2 in activities:
                if act2 != act:
                    if act2 not in act_counter:
                        rules[__rule_alternate_response(act, act2)] = -1
                    else:
                        is_ok_alt_resp = False
                        if len(act_idxs[act]) == len(act_idxs[act2]):
                            lenn = len(act_idxs[act])
                            is_ok_alt_resp = True

                            for i in range(lenn):
                                if act_idxs[act][i] > act_idxs[act2][i] or (
                                        i < lenn - 1 and act_idxs[act][i + 1] < act_idxs[act2][i]):
                                    is_ok_alt_resp = False
                                    break
                                elif act_idxs[act][i] + 1 != act_idxs[act2][i]:
                                    pass
                        rules[__rule_alternate_response(act, act2)] = 1 if is_ok_alt_resp else -1


def chainresponse_template_step1(rules: Dict[Union[Tuple[str, str], Tuple[str, str, str]], int], trace: Collection[str],
                                 activities: Set[str], act_counter: TCounter[str], act_idxs: Dict[str, List[int]],
                                 allowed_templates: Collection[str]):
    if CHAINRESPONSE in allowed_templates:
        for act in act_counter:
            for act2 in activities:
                if act2 != act:
                    if act2 not in act_counter:
                        rules[__rule_chain_response(act, act2)] = -1
                    else:
                        is_ok_chain_resp = False
                        if len(act_idxs[act]) == len(act_idxs[act2]):
                            lenn = len(act_idxs[act])
                            is_ok_chain_resp = True

                            for i in range(lenn):
                                if act_idxs[act][i] > act_idxs[act2][i] or (
                                        i < lenn - 1 and act_idxs[act][i + 1] < act_idxs[act2][i]):
                                    is_ok_chain_resp = False
                                    break
                                elif act_idxs[act][i] + 1 != act_idxs[act2][i]:
                                    is_ok_chain_resp = False
                                    break
                        rules[__rule_chain_response(act, act2)] = 1 if is_ok_chain_resp else -1


def altprecedence_template_step1(rules: Dict[Union[Tuple[str, str], Tuple[str, str, str]], int], trace: Collection[str],
                                 activities: Set[str], act_counter: TCounter[str], act_idxs: Dict[str, List[int]],
                                 allowed_templates: Collection[str]):
    if ALTPRECEDENCE in allowed_templates:
        for act in act_counter:
            for act2 in activities:
                if act2 != act:
                    if act2 not in act_counter:
                        pass
                    else:
                        is_ok_alt_prec = False
                        if len(act_idxs[act]) == len(act_idxs[act2]):
                            lenn = len(act_idxs[act])
                            is_ok_alt_prec = True
                            for i in range(lenn):
                                if act_idxs[act2][i] > act_idxs[act][i] or (
                                        i < lenn - 1 and act_idxs[act2][i + 1] < act_idxs[act][i]):
                                    is_ok_alt_prec = False
                                    break
                                elif act_idxs[act2][i] + 1 != act_idxs[act][i]:
                                    pass
                        rules[__rule_alternate_precedence(act2, act)] = 1 if is_ok_alt_prec else -1


def chainprecedence_template_step1(rules: Dict[Union[Tuple[str, str], Tuple[str, str, str]], int],
                                   trace: Collection[str], activities: Set[str], act_counter: TCounter[str],
                                   act_idxs: Dict[str, List[int]], allowed_templates: Collection[str]):
    if CHAINPRECEDENCE in allowed_templates:
        for act in act_counter:
            for act2 in activities:
                if act2 != act:
                    if act2 not in act_counter:
                        pass
                    else:
                        is_ok_chain_prec = False
                        if len(act_idxs[act]) == len(act_idxs[act2]):
                            lenn = len(act_idxs[act])
                            is_ok_chain_prec = True
                            # check alternate and chain response
                            for i in range(lenn):
                                if act_idxs[act2][i] > act_idxs[act][i] or (
                                        i < lenn - 1 and act_idxs[act2][i + 1] < act_idxs[act][i]):
                                    is_ok_chain_prec = False
                                    break
                                elif act_idxs[act2][i] + 1 != act_idxs[act][i]:
                                    is_ok_chain_prec = False
                                    break
                        rules[__rule_chain_precedence(act2, act)] = 1 if is_ok_chain_prec else -1


def absence_template(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                     allowed_templates: Collection[str]) -> pd.DataFrame:
    if ABSENCE in allowed_templates and EXISTENCE in allowed_templates:
        for act in activities:
            dataframe[__rule_absence_act(act)] = -1 * dataframe[__rule_existence_column(act)]
    return dataframe


def exactly_one_template_step2(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                               allowed_templates: Collection[str]) -> pd.DataFrame:
    if EXACTLY_ONE in allowed_templates:
        for act in activities:
            if __rule_exactly_one_column(act) not in columns:
                dataframe[__rule_exactly_one_column(act)] = [0] * len(dataframe)
    return dataframe


def responded_existence_template_step2(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                                       allowed_templates: Collection[str]) -> pd.DataFrame:
    if RESPONDED_EXISTENCE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    if __rule_responded_existence_column(act, act2) not in columns:
                        dataframe[__rule_responded_existence_column(act, act2)] = [0] * len(dataframe)
    return dataframe


def response_template_step2(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                            allowed_templates: Collection[str]) -> pd.DataFrame:
    if RESPONSE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    if __rule_response(act, act2) not in columns:
                        dataframe[__rule_response(act, act2)] = [0] * len(dataframe)
    return dataframe


def precedence_template_step2(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                              allowed_templates: Collection[str]) -> pd.DataFrame:
    if PRECEDENCE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    if __rule_precedence(act, act2) not in columns:
                        dataframe[__rule_precedence(act, act2)] = [0] * len(dataframe)
    return dataframe


def altresponse_template_step2(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                               allowed_templates: Collection[str]) -> pd.DataFrame:
    if ALTRESPONSE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    if __rule_alternate_response(act, act2) not in columns:
                        dataframe[__rule_alternate_response(act, act2)] = [0] * len(dataframe)
    return dataframe


def chainresponse_template_step2(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                                 allowed_templates: Collection[str]) -> pd.DataFrame:
    if CHAINRESPONSE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    if __rule_chain_response(act, act2) not in columns:
                        dataframe[__rule_chain_response(act, act2)] = [0] * len(dataframe)
    return dataframe


def altprecedence_template_step2(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                                 allowed_templates: Collection[str]) -> pd.DataFrame:
    if ALTPRECEDENCE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    if __rule_alternate_precedence(act, act2) not in columns:
                        dataframe[__rule_alternate_precedence(act, act2)] = [0] * len(dataframe)
    return dataframe


def chainprecedence_template_step2(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                                   allowed_templates: Collection[str]) -> pd.DataFrame:
    if CHAINPRECEDENCE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    if __rule_chain_precedence(act, act2) not in columns:
                        dataframe[__rule_chain_precedence(act, act2)] = [0] * len(dataframe)
    return dataframe


def succession_template(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                        allowed_templates: Collection[str]) -> pd.DataFrame:
    if SUCCESSION in allowed_templates and RESPONSE in allowed_templates and PRECEDENCE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    dataframe[__rule_succession(act, act2)] = dataframe[
                        [__rule_response(act, act2), __rule_precedence(act, act2)]].min(axis=1)
    return dataframe


def altsuccession_template(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                           allowed_templates: Collection[str]) -> pd.DataFrame:
    if ALTSUCCESSION in allowed_templates and ALTRESPONSE in allowed_templates and ALTPRECEDENCE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    dataframe[__rule_alternate_succession(act, act2)] = dataframe[
                        [__rule_alternate_response(act, act2), __rule_alternate_precedence(act, act2)]].min(axis=1)
    return dataframe


def chainsuccession_template(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                             allowed_templates: Collection[str]) -> pd.DataFrame:
    if CHAINSUCCESSION in allowed_templates and CHAINRESPONSE in allowed_templates and CHAINPRECEDENCE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    dataframe[__rule_chain_succession(act, act2)] = dataframe[
                        [__rule_chain_response(act, act2), __rule_chain_precedence(act, act2)]].min(axis=1)
    return dataframe


def coexistence_template(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                         allowed_templates: Collection[str]) -> pd.DataFrame:
    if COEXISTENCE in allowed_templates and RESPONDED_EXISTENCE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    dataframe[__rule_coexistence(act, act2)] = dataframe[[__rule_responded_existence_column(act, act2),
                                                                          __rule_responded_existence_column(act2,
                                                                                                            act)]].min(
                        axis=1)
    return dataframe


def noncoexistence_template(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                            allowed_templates: Collection[str]) -> pd.DataFrame:
    if NONCOEXISTENCE in allowed_templates and COEXISTENCE in allowed_templates and RESPONDED_EXISTENCE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    dataframe[__rule_non_coexistence(act, act2)] = -1 * dataframe[__rule_coexistence(act, act2)]
    return dataframe


def nonsuccession_template(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                           allowed_templates: Collection[str]) -> pd.DataFrame:
    if NONSUCCESSION in allowed_templates and SUCCESSION in allowed_templates and RESPONSE in allowed_templates and PRECEDENCE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    dataframe[__rule_non_succession(act, act2)] = -1 * dataframe[__rule_succession(act, act2)]
    return dataframe


def nonchainsuccession_template(dataframe: pd.DataFrame, columns: Collection[str], activities: Set[str],
                                allowed_templates: Collection[str]) -> pd.DataFrame:
    if NONCHAINSUCCESSION in allowed_templates and CHAINSUCCESSION in allowed_templates and CHAINRESPONSE in allowed_templates and CHAINPRECEDENCE in allowed_templates:
        for act in activities:
            for act2 in activities:
                if act2 != act:
                    dataframe[__rule_non_chain_succession(act, act2)] = -1 * dataframe[
                        __rule_chain_succession(act, act2)]
    return dataframe


def form_rules_dataframe(log: Union[EventLog, pd.DataFrame],
                         parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)

    allowed_templates = exec_utils.get_param_value(Parameters.ALLOWED_TEMPLATES, parameters, None)

    if allowed_templates is None:
        allowed_templates = {EXISTENCE, EXACTLY_ONE, INIT, RESPONDED_EXISTENCE, RESPONSE, PRECEDENCE, SUCCESSION,
                             ALTRESPONSE, ALTPRECEDENCE, ALTSUCCESSION, CHAINRESPONSE, CHAINPRECEDENCE, CHAINSUCCESSION,
                             ABSENCE, COEXISTENCE}

    import pm4py

    projected_log = pm4py.project_on_event_attribute(log, activity_key, case_id_key=case_id_key)
    activities = exec_utils.get_param_value(Parameters.CONSIDERED_ACTIVITIES, parameters, None)

    if activities is None:
        activities = set(y for x in projected_log for y in x)

    allowed_templates = set(allowed_templates)
    activities = set(activities)

    vars = Counter([tuple([y for y in x if y in activities]) for x in projected_log])
    dataframe = []

    for trace, occs in vars.items():
        act_counter = Counter(trace)
        act_idxs = {x: [] for x in set(trace)}

        for idx, act in enumerate(trace):
            act_idxs[act].append(idx)

        rules = {}

        existence_template_step1(rules, trace, activities, act_counter, act_idxs, allowed_templates)
        exactly_one_template_step1(rules, trace, activities, act_counter, act_idxs, allowed_templates)
        init_template_step1(rules, trace, activities, act_counter, act_idxs, allowed_templates)
        responded_existence_template_step1(rules, trace, activities, act_counter, act_idxs, allowed_templates)
        response_template_step1(rules, trace, activities, act_counter, act_idxs, allowed_templates)
        precedence_template_step1(rules, trace, activities, act_counter, act_idxs, allowed_templates)
        altresponse_template_step1(rules, trace, activities, act_counter, act_idxs, allowed_templates)
        chainresponse_template_step1(rules, trace, activities, act_counter, act_idxs, allowed_templates)
        altprecedence_template_step1(rules, trace, activities, act_counter, act_idxs, allowed_templates)
        chainprecedence_template_step1(rules, trace, activities, act_counter, act_idxs, allowed_templates)

        for i in range(occs):
            dataframe.append(rules)

    dataframe = pd.DataFrame(dataframe)
    dataframe.fillna(0, inplace=True)
    columns = set(dataframe.columns)

    dataframe = absence_template(dataframe, columns, activities, allowed_templates)
    dataframe = exactly_one_template_step2(dataframe, columns, activities, allowed_templates)
    dataframe = responded_existence_template_step2(dataframe, columns, activities, allowed_templates)
    dataframe = response_template_step2(dataframe, columns, activities, allowed_templates)
    dataframe = precedence_template_step2(dataframe, columns, activities, allowed_templates)
    dataframe = altresponse_template_step2(dataframe, columns, activities, allowed_templates)
    dataframe = chainresponse_template_step2(dataframe, columns, activities, allowed_templates)
    dataframe = altprecedence_template_step2(dataframe, columns, activities, allowed_templates)
    dataframe = chainprecedence_template_step2(dataframe, columns, activities, allowed_templates)

    dataframe = succession_template(dataframe, columns, activities, allowed_templates)
    dataframe = altsuccession_template(dataframe, columns, activities, allowed_templates)
    dataframe = chainsuccession_template(dataframe, columns, activities, allowed_templates)
    dataframe = coexistence_template(dataframe, columns, activities, allowed_templates)
    dataframe = noncoexistence_template(dataframe, columns, activities, allowed_templates)
    dataframe = nonsuccession_template(dataframe, columns, activities, allowed_templates)
    dataframe = nonchainsuccession_template(dataframe, columns, activities, allowed_templates)

    return dataframe


def get_rules_from_rules_df(rules_df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> Dict[
    str, Dict[Any, Dict[str, int]]]:
    if parameters is None:
        parameters = {}

    min_support_ratio = exec_utils.get_param_value(Parameters.MIN_SUPPORT_RATIO, parameters, None)
    min_confidence_ratio = exec_utils.get_param_value(Parameters.MIN_CONFIDENCE_RATIO, parameters, None)
    rules = {}

    if min_support_ratio is None and min_confidence_ratio is None:
        # auto determine the minimum support and confidence ratio by identifying the values for the best feature
        auto_selection_multiplier = exec_utils.get_param_value(Parameters.AUTO_SELECTION_MULTIPLIER, parameters, 0.8)
        cols_prod = []
        for col_name in rules_df:
            col = rules_df[col_name]
            supp = len(col[col != 0])
            supp_ratio = float(supp) / float(len(rules_df))
            if supp_ratio > 0:
                conf_ratio = float(len(col[col == 1])) / float(supp)
                prod = supp_ratio * conf_ratio
                cols_prod.append((col_name, prod))
        cols_prod = sorted(cols_prod, key=lambda x: (x[1], x[0]), reverse=True)
        col = rules_df[cols_prod[0][0]]
        supp = len(col[col != 0])
        min_support_ratio = float(supp) / float(len(rules_df)) * auto_selection_multiplier
        min_confidence_ratio = float(len(col[col == 1])) / float(supp) * auto_selection_multiplier

    for col_name in rules_df:
        col = rules_df[col_name]
        supp = len(col[col != 0])

        if supp > len(rules_df) * min_support_ratio:
            conf = len(col[col == 1])

            if conf > supp * min_confidence_ratio:
                rule, key = __col_to_dict_rule(col_name)
                if rule not in rules:
                    rules[rule] = {}

                rules[rule][key] = {"support": supp, "confidence": conf}

    return rules


def apply(log: Union[EventLog, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> Dict[
    str, Dict[Any, Dict[str, int]]]:
    """
    Discovers a DECLARE model from the provided event log

    Paper:
    F. M. Maggi, A. J. Mooij and W. M. P. van der Aalst, "User-guided discovery of declarative process models," 2011 IEEE Symposium on Computational Intelligence and Data Mining (CIDM), Paris, France, 2011, pp. 192-199, doi: 10.1109/CIDM.2011.5949297.


    Parameters
    ---------------
    log
        Log object (EventLog, Pandas dataframe)
    parameters
        Possible parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY
        - Parameters.CONSIDERED_ACTIVITIES
        - Parameters.MIN_SUPPORT_RATIO
        - Parameters.MIN_CONFIDENCE_RATIO
        - Parameters.AUTO_SELECTION_MULTIPLIER
        - Parameters.ALLOWED_TEMPLATES: collection of templates to consider, including:
            * existence
            * exactly_one
            * init
            * responded_existence
            * response
            * precedence
            * succession
            * altresponse
            * altprecedence
            * altsuccession
            * chainresponse
            * chainprecedence
            * chainsuccession
            * absence
            * coexistence
            * noncoexistence
            * nonsuccession
            * nonchainsuccession

    Returns
    -------------
    declare_model
        DECLARE model (as Python dictionary), where each template is associated with its own rules
    """
    if parameters is None:
        parameters = {}

    rules_df = form_rules_dataframe(log, parameters=parameters)

    rules = get_rules_from_rules_df(rules_df, parameters=parameters)

    return rules
