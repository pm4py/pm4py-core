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

from pm4py.util import exec_utils
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.xes_constants import DEFAULT_NAME_KEY

from typing import Optional, Dict, Any, Union, List
from pm4py.objects.log.obj import EventLog
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"


def apply(log: EventLog, admitted_start_activities: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Filter the log on the specified start activities

    Parameters
    -----------
    log
        log
    admitted_start_activities
        Admitted start activities
    parameters
        Algorithm parameters

    Returns
    -----------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    if positive:
        filtered_log = EventLog(
            [trace for trace in log if trace and trace[0][attribute_key] in admitted_start_activities],
            attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
            omni_present=log.omni_present, properties=log.properties)
    else:
        filtered_log = EventLog(
            [trace for trace in log if trace and trace[0][attribute_key] not in admitted_start_activities],
            attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
            omni_present=log.omni_present, properties=log.properties)

    return filtered_log


def filter_log_by_start_activities(start_activities, variants, vc, threshold, activity_key="concept:name"):
    """
    Keep only variants of the log with a start activity which number of occurrences is above the threshold
    
    Parameters
    ----------
    start_activities
        Dictionary of start attributes associated with their count
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    vc
        List of variant names along with their count
    threshold
        Cutting threshold (remove variants having start attributes which number of occurrences is below the threshold
    activity_key
        (If specified) Specify the activity key in the log (default concept:name)
    
    Returns
    ----------
    filtered_log
        Filtered log
    """
    filtered_log = EventLog()
    fvsa = variants[vc[0][0]][0][0][activity_key]
    for variant in variants:
        vsa = variants[variant][0][0][activity_key]
        if vsa in start_activities:
            if vsa == fvsa or start_activities[vsa] >= threshold:
                for trace in variants[variant]:
                    filtered_log.append(trace)
    return filtered_log
