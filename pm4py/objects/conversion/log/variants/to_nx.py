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
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Optional, Dict, Any, Union
from pm4py.util import exec_utils, nx_utils
from pm4py.objects.conversion.log.variants import to_event_log


class Parameters(Enum):
    INCLUDE_DF = "include_df"
    CASE_ID_ATTRIBUTE = "case_id_attribute"
    OTHER_CASE_ATTRIBUTES_AS_NODES = "other_case_attributes_as_nodes"
    EVENT_ATTRIBUTES_AS_NODES = "event_attributes_as_nodes"


def apply(log_obj: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None):
    """
    Converts an event log object to a NetworkX DiGraph object.
    The nodes of the graph are the events, the cases (and possibly the attributes of the log).
    The edges are:
    - Connecting each event to the corresponding case (BELONGS_TO type)
    - Connecting every event to the directly-following one (DF type, if enabled)
    - Connecting every case/event to the given attribute values (ATTRIBUTE_EDGE type)

    Parameters
    ----------------
    log_obj
        Log object (EventLog, EventStream, Pandas dataframe)
    parameters
        Parameters of the conversion, including:
        - Parameters.INCLUDE_DF => include the directly-follows graph relation in the graph
        - Parameters.CASE_ID_ATTRIBUTE => specify which attribute at the case level should be considered the case ID
        - Parameters.OTHER_CASE_ATTRIBUTES_AS_NODES => specify which attributes at the case level should be inserted in the graph as nodes (other than the caseID) (list, default empty)
        - Parameters.EVENT_ATTRIBUTES_AS_NODES => specify which attributes at the event level should be inserted in the graph as nodes (list, default empty)

    Returns
    ----------------
    nx_digraph
        NetworkX DiGraph object
    """
    if parameters is None:
        parameters = {}

    include_df = exec_utils.get_param_value(Parameters.INCLUDE_DF, parameters, True)
    case_id_attribute = exec_utils.get_param_value(Parameters.CASE_ID_ATTRIBUTE, parameters, "concept:name")
    other_case_attributes_as_nodes = exec_utils.get_param_value(Parameters.OTHER_CASE_ATTRIBUTES_AS_NODES, parameters, None)
    event_attributes_as_nodes = exec_utils.get_param_value(Parameters.EVENT_ATTRIBUTES_AS_NODES, parameters, None)

    parameters["stream_postprocessing"] = True
    log_obj = to_event_log.apply(log_obj, parameters=parameters)

    if event_attributes_as_nodes is None:
        event_attributes_as_nodes = []
    if other_case_attributes_as_nodes is None:
        other_case_attributes_as_nodes = []

    nx_digraph = nx_utils.DiGraph()

    for case in log_obj:
        case_id = "CASE="+str(case.attributes[case_id_attribute])
        dct_case = {"type": "CASE"}
        for att in case.attributes:
            dct_case[att] = case.attributes[att]
        nx_digraph.add_node(case_id, attr=dct_case)

        for index, event in enumerate(case):
            dct_ev = {"type": "EVENT"}
            for att in event:
                dct_ev[att] = event[att]

            ev_id = "EVENT="+str(case.attributes[case_id_attribute])+"_"+str(index)
            nx_digraph.add_node(ev_id, attr=dct_ev)
            nx_digraph.add_edge(ev_id, case_id, attr={"type": "BELONGS_TO"})

            for ev_att in event_attributes_as_nodes:
                if ev_att in event:
                    node_id = event[ev_att]
                    if node_id not in nx_digraph.nodes:
                        nx_digraph.add_node(node_id, attr={"type": "ATTRIBUTE_NODE"})
                    nx_digraph.add_edge(ev_id, node_id, attr={"type": "ATTRIBUTE_EDGE", "name": ev_att})

        if include_df:
            for index in range(len(case)-1):
                curr_ev = "EVENT="+str(case.attributes[case_id_attribute])+"_"+str(index)
                next_ev = "EVENT="+str(case.attributes[case_id_attribute])+"_"+str(index+1)

                nx_digraph.add_edge(curr_ev, next_ev, attr={"type": "DF"})

        for case_att in other_case_attributes_as_nodes:
            if case_att in case.attributes:
                node_id = case.attributes[case_att]
                if node_id not in nx_digraph.nodes:
                    nx_digraph.add_node(node_id, attr={"type": "ATTRIBUTE_NODE"})
                nx_digraph.add_edge(case_id, node_id, attr={"type": "ATTRIBUTE_EDGE", "name": case_att})

    return nx_digraph
