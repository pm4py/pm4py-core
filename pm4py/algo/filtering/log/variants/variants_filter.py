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

from pm4py.statistics.variants.log.get import get_variants, \
    get_variants_sorted_by_count
from pm4py.util import exec_utils
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY

from typing import Optional, Dict, Any, Union, List
from pm4py.objects.log.obj import EventLog
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"


def apply(log: EventLog, admitted_variants: List[List[str]], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Filter log keeping/removing only provided variants

    Parameters
    -----------
    log
        Log object
    admitted_variants
        Admitted variants
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log
            Parameters.POSITIVE -> Indicate if events should be kept/removed
    """

    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    variants = get_variants(log, parameters=parameters)
    log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                   omni_present=log.omni_present, properties=log.properties)
    for variant in variants:
        if (positive and variant in admitted_variants) or (not positive and variant not in admitted_variants):
            for trace in variants[variant]:
                log.append(trace)
    return log


def filter_variants_top_k(log, k, parameters=None):
    """
    Keeps the top-k variants of the log

    Parameters
    -------------
    log
        Event log
    k
        Number of variants that should be kept
    parameters
        Parameters

    Returns
    -------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    variants = get_variants(log, parameters=parameters)
    variant_count = get_variants_sorted_by_count(variants)
    variant_count = variant_count[:min(k, len(variant_count))]
    variants_to_filter = [x[0] for x in variant_count]

    return apply(log, variants_to_filter, parameters=parameters)


def filter_variants_by_coverage_percentage(log, min_coverage_percentage, parameters=None):
    """
    Filters the variants of the log by a coverage percentage
    (e.g., if min_coverage_percentage=0.4, and we have a log with 1000 cases,
    of which 500 of the variant 1, 400 of the variant 2, and 100 of the variant 3,
    the filter keeps only the traces of variant 1 and variant 2).

    Parameters
    ---------------
    log
        Event log
    min_coverage_percentage
        Minimum allowed percentage of coverage
    parameters
        Parameters

    Returns
    ---------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    variants = get_variants(log, parameters=parameters)
    variants = {x: len(y) for x, y in variants.items()}
    allowed_variants = [x for x, y in variants.items() if y >= min_coverage_percentage * len(log)]

    return apply(log, allowed_variants, parameters=parameters)


def filter_variants_by_maximum_coverage_percentage(log, max_coverage_percentage, parameters=None):
    """
    Filters the variants of the log by a maximum coverage percentage
    (e.g., if max_coverage_percentage=0.4, and we have a log with 1000 cases,
    of which 500 of the variant 1, 400 of the variant 2, and 100 of the variant 3,
    the filter keeps only the traces of variant 2 and variant 3).

    Parameters
    ---------------
    log
        Event log
    max_coverage_percentage
        Maximum allowed percentage of coverage
    parameters
        Parameters

    Returns
    ---------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    variants = get_variants(log, parameters=parameters)
    variants = {x: len(y) for x, y in variants.items()}
    allowed_variants = [x for x, y in variants.items() if y <= max_coverage_percentage * len(log)]

    return apply(log, allowed_variants, parameters=parameters)


def filter_log_variants_percentage(log, percentage=0.8, parameters=None):
    """
    Filters a log by variants percentage

    Parameters
    -------------
    log
        Event log
    percentage
        Percentage
    parameters
        Parameters of the algorithm

    Returns
    -------------
    filtered_log
        Filtered log (by variants percentage)
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    variants = get_variants(log, parameters=parameters)

    return filter_variants_variants_percentage(log, variants, variants_percentage=percentage)


def filter_variants_variants_percentage(log, variants, variants_percentage=0.0):
    """
    Filter the log by variants percentage

    Parameters
    ----------
    log
        Log
    variants
        Dictionary with variant as the key and the list of traces as the value
    variants_percentage
        Percentage of variants that should be kept (the most common variant is always kept)

    Returns
    ----------
    filtered_log
        Filtered log
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    filtered_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present, properties=log.properties)
    no_of_traces = len(log)
    variant_count = get_variants_sorted_by_count(variants)
    already_added_sum = 0
    shall_break_under = -1

    for i in range(len(variant_count)):
        variant = variant_count[i][0]
        varcount = variant_count[i][1]
        if varcount < shall_break_under:
            break
        for trace in variants[variant]:
            filtered_log.append(trace)
        already_added_sum = already_added_sum + varcount
        percentage_already_added = already_added_sum / no_of_traces
        if percentage_already_added >= variants_percentage:
            shall_break_under = varcount

    return filtered_log


def find_auto_threshold(log, variants, decreasing_factor):
    """
    Find automatically variants filtering threshold
    based on specified decreasing factor
    
    Parameters
    ----------
    log
        Log
    variants
        Dictionary with variant as the key and the list of traces as the value
    decreasing_factor
        Decreasing factor (stops the algorithm when the next variant by occurrence is below this factor
        in comparison to previous)
    
    Returns
    ----------
    variantsPercentage
        Percentage of variants to keep in the log
    """
    no_of_traces = len(log)
    variant_count = get_variants_sorted_by_count(variants)
    already_added_sum = 0

    prev_var_count = -1
    percentage_already_added = 0
    for i in range(len(variant_count)):
        varcount = variant_count[i][1]
        percentage_already_added = already_added_sum / no_of_traces
        if already_added_sum == 0 or varcount > decreasing_factor * prev_var_count:
            already_added_sum = already_added_sum + varcount
        else:
            break
        prev_var_count = varcount

    percentage_already_added = already_added_sum / no_of_traces

    return percentage_already_added
