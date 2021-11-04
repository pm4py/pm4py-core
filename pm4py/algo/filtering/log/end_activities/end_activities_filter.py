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

from pm4py.algo.filtering.common import filtering_constants
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.obj import EventLog
from pm4py.statistics.end_activities.common import get as end_activities_common
from pm4py.statistics.end_activities.log.get import get_end_activities
from pm4py.util import exec_utils
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
import deprecation

from typing import Optional, Dict, Any, Union, Tuple, List
from pm4py.objects.log.obj import EventLog, EventStream, Trace


class Parameters(Enum):
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"


def apply(log: EventLog, admitted_end_activities: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Filter the log on the specified end activities

    Parameters
    -----------
    log
        Log
    admitted_end_activities
        Admitted end activities
    parameters
        Algorithm parameters

    Returns
    -----------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}
    attribute_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    if positive:
        filtered_log = [trace for trace in log if trace and trace[-1][attribute_key] in admitted_end_activities]
    else:
        filtered_log = [trace for trace in log if trace and trace[-1][attribute_key] not in admitted_end_activities]

    return EventLog(filtered_log, attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                    omni_present=log.omni_present, properties=log.properties)


def filter_log_by_end_activities(end_activities, variants, vc, threshold, activity_key="concept:name"):
    """
    Keep only variants of the log with an end activity which number of occurrences is above the threshold
    
    Parameters
    ----------
    end_activities
        Dictionary of end attributes associated with their count
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    vc
        List of variant names along with their count
    threshold
        Cutting threshold (remove variants having end attributes which number of occurrences is below the threshold
    activity_key
        (If specified) Specify the activity key in the log (default concept:name)
    
    Returns
    ----------
    filtered_log
        Filtered log
    """
    filtered_log = EventLog()
    fvea = variants[vc[0][0]][0][-1][activity_key]
    for variant in variants:
        vea = variants[variant][0][-1][activity_key]
        if vea in end_activities:
            if vea == fvea or end_activities[vea] >= threshold:
                for trace in variants[variant]:
                    filtered_log.append(trace)
    return filtered_log


@deprecation.deprecated("2.2.11", "3.0.0", details="Removed")
def apply_auto_filter(log, variants=None, parameters=None):
    """
    Apply an end attributes filter detecting automatically a percentage
    
    Parameters
    ----------
    log
        Log
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    parameters
        Parameters of the algorithm, including:
            Parameters.DECREASING_FACTOR -> Decreasing factor (stops the algorithm when the next activity by occurrence is below
            this factor in comparison to previous)
            Parameters.ACTIVITY_KEY -> Attribute key (must be specified if different from concept:name)
    
    Returns
    ---------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    attribute_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    decreasing_factor = exec_utils.get_param_value(Parameters.DECREASING_FACTOR, parameters,
                                                   filtering_constants.DECREASING_FACTOR)

    if len(log) > 0:
        parameters_variants = {PARAMETER_CONSTANT_ACTIVITY_KEY: attribute_key}
        if variants is None:
            variants = variants_filter.get_variants(log, parameters=parameters_variants)
        vc = variants_filter.get_variants_sorted_by_count(variants)
        end_activities = get_end_activities(log, parameters=parameters_variants)
        ealist = end_activities_common.get_sorted_end_activities_list(end_activities)
        eathreshold = end_activities_common.get_end_activities_threshold(ealist, decreasing_factor)
        filtered_log = filter_log_by_end_activities(end_activities, variants, vc, eathreshold, attribute_key)

        return filtered_log

    return log
