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
from typing import Optional, Dict, Any, Tuple, Union

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils, constants, xes_constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ATTRIBUTES = "case_attributes"
    RETURN_NODES_ATTRIBUTES = "return_nodes_attributes"


def apply(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Union[
    Tuple[Dict[Tuple[str, str], Dict[str, Dict[str, Any]]], Dict[str, Dict[str, Dict[str, Any]]]], Dict[
        Tuple[str, str], Dict[str, Dict[str, Any]]]]:
    """
    Discovers a directly-follows graph from an event log, with the edges that are annotated with the different values
    for the given case attributes.

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the variant, including:
        - Parameters.ACTIVITY_KEY => the attribute to use as activity
        - Parameters.CASE_ATTRIBUTES => the case attributes that are used to annotate the edges (default: the case ID)
        - Parameters.RETURN_NODES_ATTRIBUTES => (optional) returns also a dictionary with the values of the
        attributes for each activity of the graph (default: False)

    Returns
    -----------------
    dfg
        Directly-follows graph (with the edges annotated with the specified case attributes), e.g.:
            {('register request', 'examine casually'): {'creator': {'Fluxicon Nitro': 3}, 'concept:name':
                {'3': 1, '6': 1, '5': 1}} ...
    nodes
        (Optional) dictionary of activities (annotated with the specified case attributes), e.g.:
            {'register request': {'creator': {'Fluxicon Nitro': 6}, 'concept:name':
                {'3': 1, '2': 1, '1': 1, '6': 1, '5': 1, '4': 1}} ...
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    case_attributes = exec_utils.get_param_value(Parameters.CASE_ATTRIBUTES, parameters,
                                                 list([xes_constants.DEFAULT_TRACEID_KEY]))
    return_nodes_attributes = exec_utils.get_param_value(Parameters.RETURN_NODES_ATTRIBUTES, parameters, False)
    dfg = {}

    for trace in log:
        for attr in set(case_attributes).intersection(set(trace.attributes)):
            attr_value = trace.attributes[attr]
            for i in range(len(trace) - 1):
                ev_couple = (trace[i][activity_key], trace[i + 1][activity_key])
                if ev_couple not in dfg:
                    dfg[ev_couple] = {}
                if attr not in dfg[ev_couple]:
                    dfg[ev_couple][attr] = {}
                if attr_value not in dfg[ev_couple][attr]:
                    dfg[ev_couple][attr][attr_value] = 0
                dfg[ev_couple][attr][attr_value] += 1

    if return_nodes_attributes:
        nodes = {}
        for trace in log:
            for attr in set(case_attributes).intersection(set(trace.attributes)):
                attr_value = trace.attributes[attr]
                for i in range(len(trace)):
                    act = trace[i][activity_key]
                    if act not in nodes:
                        nodes[act] = {}
                    if attr not in nodes[act]:
                        nodes[act][attr] = {}
                    if attr_value not in nodes[act][attr]:
                        nodes[act][attr][attr_value] = 0
                    nodes[act][attr][attr_value] += 1

        return dfg, nodes

    return dfg
