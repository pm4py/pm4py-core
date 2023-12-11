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
import re
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Any, Union, List
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.filtering.common.traces.infix_to_regex import translate_infix_to_regex
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    POSITIVE = "positive"


def apply(log: Union[EventLog, EventStream, pd.DataFrame], admitted_traces: List[List[str]], parameters: Optional[Dict[Any, Any]] = None) -> EventLog:
    """
    Filters an event log on a set of traces. A trace is a sequence of activities and "...", in which:
    - a "..." before an activity tells that other activities can precede the given activity
    - a "..." after an activity tells that other activities can follow the given activity

    For example:
    - apply(log, [["A", "B"]]) <- filters only the cases of the event log having exactly the process variant A,B
    - apply(log, [["...", "A", "B"]]) <- filters only the cases of the event log ending with the activities A,B
    - apply(log, [["A", "B", "..."]]) <- filters only the cases of the event log starting with the activities A,B
    - apply(log, [["...", "A", "B", "C", "..."], ["...", "D", "E", "F", "..."]]
                                <- filters only the cases of the event log in which at any point
                                    there is A followed by B followed by C, and in which at any other point there is
                                    D followed by E followed by F

    Parameters
    -----------------
    log
        Event log
    admitted_traces
        Collection of traces admitted from the filter (with the aforementioned criteria)
    parameters
        Parameters of the method, including:
        - Parameters.ACTIVITY_KEY => the attribute that should be used as activity
        - Parameters.POSITIVE => indicates if the filter should keep/discard the cases satisfying the filter
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    filter_regex = "|".join([f"({translate_infix_to_regex(inf)})" for inf in admitted_traces])
    filtered_log = EventLog(attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
            omni_present=log.omni_present, properties=log.properties)

    for case in log:
        t = constants.DEFAULT_VARIANT_SEP.join([x[activity_key] for x in case])
        found = bool(re.search(filter_regex, t))
        if (positive and found) or (not positive and not found):
            filtered_log.append(case)

    return filtered_log
