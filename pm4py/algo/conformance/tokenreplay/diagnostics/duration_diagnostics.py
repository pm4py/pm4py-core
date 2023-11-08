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

from pm4py.objects.log.util import basic_filter
from pm4py.util import xes_constants as xes

from statistics import median
from enum import Enum
from pm4py.util import exec_utils
from pm4py.util import constants
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


def get_case_duration(case, timestamp_key=xes.DEFAULT_TIMESTAMP_KEY):
    """
    Gets the duration of a case

    Parameters
    -------------
    case
        Case
    timestamp_key
        Attribute of the event to use as timestamp

    Returns
    -------------
    case_duration
        Case duration
    """
    return (case[-1][timestamp_key] - case[0][timestamp_key]).total_seconds()


def get_median_case_duration(list_cases, timestamp_key=xes.DEFAULT_TIMESTAMP_KEY):
    """
    Gets the median case duration of a list of cases

    Parameters
    -------------
    list_cases
        List of cases
    timestamp_key
        Attribute of the event to use as timestamp

    Returns
    -------------
    median_case_duration
        Median case duration
    """
    durations = []
    for trace in list_cases:
        durations.append(get_case_duration(trace, timestamp_key=timestamp_key))
    return median(durations)


def diagnose_from_notexisting_activities(log, notexisting_activities_in_model, parameters=None):
    """
    Provide some conformance diagnostics related to activities that are not present in the model

    Parameters
    -------------
    log
        Trace log
    notexisting_activities_in_model
        Not existing activities in the model
    parameters
        Possible parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> attribute of the event containing the timestamp

    Returns
    -------------
    diagnostics
        For each problematic activity, diagnostics about case duration
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY)
    diagnostics = {}

    parameters_filtering = deepcopy(parameters)
    parameters_filtering["positive"] = False
    values = list(notexisting_activities_in_model.keys())

    filtered_log = basic_filter.filter_log_traces_attr(log, values, parameters=parameters_filtering)

    for act in notexisting_activities_in_model:
        fit_cases = []
        containing_cases = []
        for trace in log:
            if trace in notexisting_activities_in_model[act]:
                containing_cases.append(trace)
            elif trace in filtered_log:
                fit_cases.append(trace)
        if containing_cases and fit_cases:
            n_containing = len(containing_cases)
            n_fit = len(fit_cases)
            fit_median_time = get_median_case_duration(fit_cases, timestamp_key=timestamp_key)
            containing_median_time = get_median_case_duration(containing_cases, timestamp_key=timestamp_key)
            relative_throughput = containing_median_time / fit_median_time if fit_median_time > 0 else 0

            diagn_dict = {"n_containing": n_containing, "n_fit": n_fit, "fit_median_time": fit_median_time,
                          "containing_median_time": containing_median_time,
                          "relative_throughput": relative_throughput}
            diagnostics[act] = diagn_dict
    return diagnostics


def diagnose_from_trans_fitness(log, trans_fitness, parameters=None):
    """
    Provide some conformance diagnostics related to transitions that are executed in a unfit manner

    Parameters
    -------------
    log
        Trace log
    trans_fitness
        For each transition, keeps track of unfit executions
    parameters
        Possible parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> attribute of the event containing the timestamp

    Returns
    -------------
    diagnostics
        For each problematic transition, diagnostics about case duration
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY)
    diagnostics = {}

    parameters_filtering = deepcopy(parameters)
    parameters_filtering["positive"] = True

    for trans in trans_fitness:
        if len(trans_fitness[trans]["underfed_traces"]) > 0:
            filtered_log_act = basic_filter.filter_log_traces_attr(log, [trans.label], parameters=parameters_filtering)
            fit_cases = []
            underfed_cases = []
            for trace in log:
                if trace in trans_fitness[trans]["underfed_traces"]:
                    underfed_cases.append(trace)
                elif trace in filtered_log_act:
                    fit_cases.append(trace)
            if fit_cases and underfed_cases:
                n_fit = len(fit_cases)
                n_underfed = len(underfed_cases)
                fit_median_time = get_median_case_duration(fit_cases, timestamp_key=timestamp_key)
                underfed_median_time = get_median_case_duration(underfed_cases, timestamp_key=timestamp_key)
                relative_throughput = underfed_median_time / fit_median_time if fit_median_time > 0 else 0

                diagn_dict = {"n_fit": n_fit, "n_underfed": n_underfed, "fit_median_time": fit_median_time,
                              "underfed_median_time": underfed_median_time, "relative_throughput": relative_throughput}
                diagnostics[trans] = diagn_dict
    return diagnostics
