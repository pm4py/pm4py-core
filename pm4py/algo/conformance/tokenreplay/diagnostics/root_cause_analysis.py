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
from copy import deepcopy
from enum import Enum

import numpy as np

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.objects.log.util import basic_filter
from pm4py.util import exec_utils
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    STRING_ATTRIBUTES = "string_attributes"
    NUMERIC_ATTRIBUTES = "numeric_attributes"
    ENABLE_MULTIPLIER = "enable_multiplier"


def form_log_from_dictio_couple(first_cases_repr, second_cases_repr, enable_multiplier=False):
    """
    Form a log from a couple of dictionary, to use for
    root cause analysis

    Parameters
    -------------
    first_cases_repr
        First cases representation
    second_cases_repr
        Second cases representation
    enable_multiplier
        Enable balancing of classes

    Returns
    ------------
    log
        Trace log object
    """
    log = EventLog()

    if enable_multiplier:
        multiplier_first = int(max(float(len(second_cases_repr)) / float(len(first_cases_repr)), 1))
        multiplier_second = int(max(float(len(first_cases_repr)) / float(len(second_cases_repr)), 1))
    else:
        multiplier_first = 1
        multiplier_second = 1

    for j in range(multiplier_first):
        for i in range(len(first_cases_repr)):
            trace = Trace()
            event = Event(first_cases_repr[i])
            trace.append(event)
            log.append(trace)

    for j in range(multiplier_second):
        for i in range(len(second_cases_repr)):
            trace = Trace()
            event = Event(second_cases_repr[i])
            trace.append(event)
            log.append(trace)

    return log


def form_representation_from_dictio_couple(first_cases_repr, second_cases_repr, string_attributes, numeric_attributes,
                                           enable_multiplier=False):
    """
    Gets a log representation, useful for training the decision tree,
    from a couple of dictionaries along with the list of string attributes
    and numeric attributes to consider, to use for root cause analysis

    Parameters
    ------------
    first_cases_repr
        First cases representation
    second_cases_repr
        Second cases representation
    string_attributes
        String attributes contained in the log
    numeric_attributes
        Numeric attributes contained in the log
    enable_multiplier
        Enable balancing of classes

    Returns
    ------------
    data
        Matrix representation of the event log
    feature_names
        Array of feature names
    """
    from pm4py.algo.transformation.log_to_features import algorithm as log_to_features

    log = form_log_from_dictio_couple(first_cases_repr, second_cases_repr,
                                      enable_multiplier=enable_multiplier)

    data, feature_names = log_to_features.apply(log, variant=log_to_features.Variants.TRACE_BASED,
                                                parameters={"str_tr_attr": [], "str_ev_attr": string_attributes,
                                                            "num_tr_attr": [], "num_ev_attr": numeric_attributes})

    return data, feature_names


def diagnose_from_trans_fitness(log, trans_fitness, parameters=None):
    """
    Perform root cause analysis starting from transition fitness knowledge

    Parameters
    -------------
    log
        Trace log object
    trans_fitness
        Transition fitness object
    parameters
        Possible parameters of the algorithm, including:
            string_attributes -> List of string event attributes to consider
                in building the decision tree
            numeric_attributes -> List of numeric event attributes to consider
                in building the decision tree

    Returns
    -----------
    diagnostics
        For each problematic transition:
            - a decision tree comparing fit and unfit executions
            - feature names
            - classes
    """
    from pm4py.util import ml_utils

    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    diagnostics = {}
    string_attributes = exec_utils.get_param_value(Parameters.STRING_ATTRIBUTES, parameters, [])
    numeric_attributes = exec_utils.get_param_value(Parameters.NUMERIC_ATTRIBUTES, parameters, [])
    enable_multiplier = exec_utils.get_param_value(Parameters.ENABLE_MULTIPLIER, parameters, False)

    for trans in trans_fitness:
        if len(trans_fitness[trans]["underfed_traces"]) > 0:
            fit_cases_repr = []
            underfed_cases_repr = []

            for trace in log:
                if trace in trans_fitness[trans]["underfed_traces"]:
                    underfed_cases_repr.append(trans_fitness[trans]["underfed_traces"][trace][0])
                elif trace in trans_fitness[trans]["fit_traces"]:
                    fit_cases_repr.append(trans_fitness[trans]["fit_traces"][trace][0])

            if fit_cases_repr and underfed_cases_repr:
                data, feature_names = form_representation_from_dictio_couple(fit_cases_repr, underfed_cases_repr,
                                                                             string_attributes, numeric_attributes,
                                                                             enable_multiplier=enable_multiplier)
                target = []
                classes = []

                if enable_multiplier:
                    multiplier_first = int(max(float(len(underfed_cases_repr)) / float(len(fit_cases_repr)), 1))
                    multiplier_second = int(max(float(len(fit_cases_repr)) / float(len(underfed_cases_repr)), 1))
                else:
                    multiplier_first = 1
                    multiplier_second = 1

                for j in range(multiplier_first):
                    for i in range(len(fit_cases_repr)):
                        target.append(0)
                classes.append("fit")

                for j in range(multiplier_second):
                    for i in range(len(underfed_cases_repr)):
                        target.append(1)
                classes.append("underfed")

                data = np.array([np.array(x) for x in data])

                target = np.asarray(target)
                clf = ml_utils.DecisionTreeClassifier(max_depth=7)
                clf.fit(data, target)
                diagn_dict = {"clf": clf, "data": data, "feature_names": feature_names, "target": target,
                              "classes": classes}

                diagnostics[trans] = diagn_dict

    return diagnostics


def diagnose_from_notexisting_activities(log, notexisting_activities_in_model, parameters=None):
    """
    Perform root cause analysis related to activities that are not present in the model

    Parameters
    -------------
    log
        Trace log object
    notexisting_activities_in_model
        Not existing activities in the model
    parameters
        Possible parameters of the algorithm, including:
            string_attributes -> List of string event attributes to consider
                in building the decision tree
            numeric_attributes -> List of numeric event attributes to consider
                in building the decision tree

    Returns
    -----------
    diagnostics
        For each problematic transition:
            - a decision tree comparing fit and unfit executions
            - feature names
            - classes
    """
    from pm4py.util import ml_utils

    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    diagnostics = {}
    string_attributes = exec_utils.get_param_value(Parameters.STRING_ATTRIBUTES, parameters, [])
    numeric_attributes = exec_utils.get_param_value(Parameters.NUMERIC_ATTRIBUTES, parameters, [])
    enable_multiplier = exec_utils.get_param_value(Parameters.ENABLE_MULTIPLIER, parameters, False)

    parameters_filtering = deepcopy(parameters)
    parameters_filtering["positive"] = False
    values = list(notexisting_activities_in_model.keys())

    filtered_log = basic_filter.filter_log_traces_attr(log, values, parameters=parameters_filtering)

    for act in notexisting_activities_in_model:
        fit_cases_repr = []
        containing_cases_repr = []
        for trace in log:
            if trace in notexisting_activities_in_model[act]:
                containing_cases_repr.append(notexisting_activities_in_model[act][trace])
            elif trace in filtered_log:
                fit_cases_repr.append(dict(trace[-1]))

        if fit_cases_repr and containing_cases_repr:
            data, feature_names = form_representation_from_dictio_couple(fit_cases_repr, containing_cases_repr,
                                                                         string_attributes, numeric_attributes,
                                                                         enable_multiplier=enable_multiplier)

            target = []
            classes = []

            if enable_multiplier:
                multiplier_first = int(max(float(len(containing_cases_repr)) / float(len(fit_cases_repr)), 1))
                multiplier_second = int(max(float(len(fit_cases_repr)) / float(len(containing_cases_repr)), 1))
            else:
                multiplier_first = 1
                multiplier_second = 1

            for j in range(multiplier_first):
                for i in range(len(fit_cases_repr)):
                    target.append(0)
            classes.append("fit")

            for j in range(multiplier_second):
                for i in range(len(containing_cases_repr)):
                    target.append(1)
            classes.append("containing")

            data = np.array([np.array(x) for x in data])

            target = np.asarray(target)
            clf = ml_utils.DecisionTreeClassifier(max_depth=7)
            clf.fit(data, target)
            diagn_dict = {"clf": clf, "data": data, "feature_names": feature_names, "target": target,
                          "classes": classes}

            diagnostics[act] = diagn_dict

    return diagnostics
