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
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.log.obj import Trace
from typing import Optional, Dict, Any


class Parameters(Enum):
    INCLUDE_CASE_ATTRIBUTES = "include_case_attributes"
    INCLUDE_EVENT_ATTRIBUTES = "include_event_attributes"
    INCLUDE_TIMESTAMP = "include_timestamp"
    INCLUDE_HEADER = "include_header"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


def apply(case: Trace, parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Provides a textual abstraction of a single case (Trace object) of a traditional event log

    Parameters
    ---------------
    case
        Single case (Trace object) of a traditional event log
    parameters
        Parameters of the method, including:
        - Parameters.INCLUDING_CASE_ATTRIBUTES
        - Parameters.INCLUDE_EVENT_ATTRIBUTES
        - Parameters.INCLUDE_TIMESTAMP
        - Parameters.INCLUDE_HEADER => includes the header (or not) in the response)
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity
        - Parameters.TIMESTAMP_KEY => the attribute to be used as timestamp

    Returns
    ---------------
    stru
        Textual abstraction of the case
    """
    if parameters is None:
        parameters = {}

    include_case_attributes = exec_utils.get_param_value(Parameters.INCLUDE_CASE_ATTRIBUTES, parameters, True)
    include_event_attributes = exec_utils.get_param_value(Parameters.INCLUDE_EVENT_ATTRIBUTES, parameters, True)
    include_timestamp = exec_utils.get_param_value(Parameters.INCLUDE_TIMESTAMP, parameters, True)
    include_header = exec_utils.get_param_value(Parameters.INCLUDE_HEADER, parameters, True)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)

    ret = ["\n"]

    if include_header:
        ret.append("If I have a case")
        if include_case_attributes:
            ret.append(" with the following (case) attributes:")
        ret.append("")

    ret.append("\n")

    if include_case_attributes:
        for k, v in case.attributes.items():
            ret.append("\n%s = %s" % (str(k), str(v)))

    ret.append("\n\n")

    if include_header:
        ret.append("\nthe case contains the following events (the activity of the event is reported first):\n\n")

    for ev in case:
        stru = "%s " % (ev[activity_key])
        ev_attrs = sorted([str(x) for x in ev if x not in [activity_key, timestamp_key]])

        if include_timestamp or (ev_attrs and include_event_attributes):
            stru += "("
            if include_timestamp:
                stru += " timestamp = " + str(ev[timestamp_key]) + " ; "

            if include_event_attributes and ev_attrs:
                for attr in ev_attrs:
                    stru += " " + attr + " = " + str(ev[attr]) + " ; "

            stru += ")"

        stru += "\n"

        ret.append(stru)

    ret.append("\n")

    return "".join(ret)
