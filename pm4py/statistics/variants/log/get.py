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
from typing import Optional, Dict, Any, Union, Tuple, List

import numpy as np

from pm4py.objects.log.obj import EventLog, Trace
from pm4py.util import constants
from pm4py.util import exec_utils, variants_util
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    MAX_NO_POINTS_SAMPLE = "max_no_of_points_to_sample"
    KEEP_ONCE_PER_CASE = "keep_once_per_case"


def get_language(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Union[
    Dict[List[str], float], Dict[str, float]]:
    """
    Gets the stochastic language of the log (from the variants)

    Parameters
    --------------
    log
        Event log
    parameters
        Parameters

    Returns
    --------------
    dictio
        Dictionary containing the stochastic language of the log
        (variant associated to a number between 0 and 1; the sum is 1)
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
    vars = get_variants(log, parameters=parameters)
    vars = {variants_util.get_activities_from_variant(x): len(y) for x, y in vars.items()}

    all_values_sum = sum(vars.values())
    for x in vars:
        vars[x] = vars[x] / all_values_sum
    return vars


def get_variants(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Union[
    Dict[List[str], List[Trace]], Dict[str, List[Trace]]]:
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces that share the variant

    Parameters
    ----------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log

    Returns
    ----------
    variant
        Dictionary with variant as the key and the list of traces as the value
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    variants_trace_idx = get_variants_from_log_trace_idx(log, parameters=parameters)

    all_var = convert_variants_trace_idx_to_trace_obj(log, variants_trace_idx)

    return all_var


def get_variants_along_with_case_durations(log: EventLog,
                                           parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[
    Union[Dict[List[str], List[Trace]], Dict[str, List[Trace]]], np.array]:
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces that share the variant

    Parameters
    ----------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log

    Returns
    ----------
    variant
        Dictionary with variant as the key and the list of traces as the value
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    variants_trace_idx = get_variants_from_log_trace_idx(log, parameters=parameters)
    all_var = convert_variants_trace_idx_to_trace_obj(log, variants_trace_idx)

    all_durations = {}

    for var in all_var:
        all_durations[var] = []
        for trace in all_var[var]:
            if trace and timestamp_key in trace[-1] and timestamp_key in trace[0]:
                all_durations[var].append((trace[-1][timestamp_key] - trace[0][timestamp_key]).total_seconds())
            else:
                all_durations[var].append(0)
        all_durations[var] = np.array(all_durations[var])

    return all_var, all_durations


def get_variants_from_log_trace_idx(log, parameters=None):
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces indexes that share the variant

    Parameters
    ----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log

    Returns
    ----------
    variant
        Dictionary with variant as the key and the list of traces indexes as the value
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    variants = {}
    for trace_idx, trace in enumerate(log):
        variant = variants_util.get_variant_from_trace(trace, parameters=parameters)
        if variant not in variants:
            variants[variant] = []
        variants[variant].append(trace_idx)

    return variants


def get_variants_sorted_by_count(variants):
    """
    From the dictionary of variants returns an ordered list of variants
    along with their count

    Parameters
    ----------
    variants
        Dictionary with variant as the key and the list of traces as the value

    Returns
    ----------
    var_count
        List of variant names along with their count
    """
    var_count = []
    for variant in variants:
        var_count.append([variant, len(variants[variant])])
    var_count = sorted(var_count, key=lambda x: (x[1], x[0]), reverse=True)
    return var_count


def convert_variants_trace_idx_to_trace_obj(log, variants_trace_idx):
    """
    Converts variants expressed as trace indexes to trace objects

    Parameters
    -----------
    log
        Trace log object
    variants_trace_idx
        Variants associated to a list of belonging indexes

    Returns
    -----------
    variants
        Variants associated to a list of belonging traces
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    variants = {}

    for key in variants_trace_idx:
        variants[key] = []
        for value in variants_trace_idx[key]:
            variants[key].append(log[value])

    return variants
