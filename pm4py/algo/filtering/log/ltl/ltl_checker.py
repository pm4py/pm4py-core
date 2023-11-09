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

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.util import exec_utils
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_RESOURCE_KEY, \
    PARAMETER_CONSTANT_TIMESTAMP_KEY
from pm4py.util.xes_constants import DEFAULT_NAME_KEY, DEFAULT_RESOURCE_KEY, DEFAULT_TIMESTAMP_KEY

from typing import Optional, Dict, Any, Union, List
from pm4py.objects.log.obj import EventLog
import itertools


class Parameters(Enum):
    ATTRIBUTE_KEY = PARAMETER_CONSTANT_ATTRIBUTE_KEY
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    RESOURCE_KEY = PARAMETER_CONSTANT_RESOURCE_KEY
    POSITIVE = "positive"
    ENABLE_TIMESTAMP = "enable_timestamp"
    TIMESTAMP_DIFF_BOUNDARIES = "timestamp_diff_boundaries"


POSITIVE = Parameters.POSITIVE
ENABLE_TIMESTAMP = Parameters.ENABLE_TIMESTAMP
TIMESTAMP_DIFF_BOUNDARIES = Parameters.TIMESTAMP_DIFF_BOUNDARIES


def timestamp_list_is_ge(a, b):
    for i in range(len(a)):
        if a[i] < b[i][0]:
            return False
    return True


def timestamp_list_is_le(a, b):
    for i in range(len(a)):
        if a[i] > b[i][1]:
            return False
    return True


def eventually_follows(log: EventLog, attribute_values: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Applies the eventually follows rule

    Parameters
    ------------
    log
        Log
    attribute_values
        A list of attribute_values attribute_values[n] follows attribute_values[n-1] follows ... follows attribute_values[0]

    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing all attribute_values and in which attribute_values[i] was eventually followed by attribute_values[i + 1]
        - If False, returns all the cases not containing all attribute_values, or in which an instance of attribute_values[i] was not eventually
        followed by an instance of attribute_values[i + 1]

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    enable_timestamp = exec_utils.get_param_value(Parameters.ENABLE_TIMESTAMP, parameters, False)
    timestamp_diff_boundaries = exec_utils.get_param_value(Parameters.TIMESTAMP_DIFF_BOUNDARIES, parameters, [])

    new_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                       omni_present=log.omni_present, properties=log.properties)

    for trace in log:
        occurrences = [[i for i in range(len(trace))
                        if attribute_key in trace[i] and trace[i][attribute_key] == attribute_value] for attribute_value in attribute_values]

        is_good = False

        for c in itertools.product(*occurrences):
            ok = True
            for i in range(len(c)-1):
                if c[i] >= c[i+1]:
                    ok = False
                    break
            if ok:
                if enable_timestamp and timestamp_diff_boundaries:
                    for i in range(len(c)-1):
                        timest_i = trace[i][timestamp_key].timestamp()
                        timest_j = trace[i+1][timestamp_key].timestamp()
                        if timest_j - timest_i < timestamp_diff_boundaries[i][0] or timest_j - timest_i > timestamp_diff_boundaries[i][1]:
                            ok = False
                            break

            if ok:
                is_good = True
                break

        if is_good:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log


def A_next_B_next_C(log: EventLog, A: str, B: str, C: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Applies the A next B next C rule

    Parameters
    ------------
    log
        Log
    A
        A attribute value
    B
        B attribute value
    C
        C attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A, B and C and in which A was directly followed by B and B was directly followed by C
        - If False, returns all the cases not containing A or B or C, or in which none instance of A was directly
        followed by an instance of B and B was directly followed by C

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    new_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                       omni_present=log.omni_present, properties=log.properties)

    for trace in log:
        occ_A = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == A]
        occ_B = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == B]
        occ_C = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == C]

        found = False

        for a in occ_A:
            for b in occ_B:
                for c in occ_C:
                    if (b - a) == 1 and (c - b) == 1:
                        found = True

        if found:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log


def four_eyes_principle(log: EventLog, A: str, B: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Verifies the Four Eyes Principle given A and B

    Parameters
    -------------
    log
        Log
    A
        A attribute value
    B
        B attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - if True, then filters all the cases containing A and B which have empty intersection between the set
          of resources doing A and B
        - if False, then filters all the cases containing A and B which have no empty intersection between the set
          of resources doing A and B

    Returns
    --------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, DEFAULT_RESOURCE_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    new_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                       omni_present=log.omni_present, properties=log.properties)

    for trace in log:
        occ_A = set([trace[i][resource_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and resource_key in trace[i] and trace[i][attribute_key] == A])
        occ_B = set([trace[i][resource_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and resource_key in trace[i] and trace[i][attribute_key] == B])

        if len(occ_A) > 0 and len(occ_B) > 0:
            inte = occ_A.intersection(occ_B)

            if not positive and len(inte) > 0:
                new_log.append(trace)
            elif positive and len(inte) == 0:
                new_log.append(trace)

    return new_log


def attr_value_different_persons(log: EventLog, A: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Checks whether an attribute value is assumed on events done by different resources

    Parameters
    ------------
    log
        Log
    A
        A attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
            - if True, then filters all the cases containing occurrences of A done by different resources
            - if False, then filters all the cases not containing occurrences of A done by different resources

    Returns
    -------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, DEFAULT_RESOURCE_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    new_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                       omni_present=log.omni_present, properties=log.properties)

    for trace in log:
        occ_A = set([trace[i][resource_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and resource_key in trace[i] and trace[i][attribute_key] == A])
        if len(occ_A) > 1:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log
