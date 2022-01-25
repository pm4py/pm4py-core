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
from typing import Union

import pandas as pd

from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties
from pm4py.util import constants, xes_constants
from typing import Dict, Tuple, Any


def discover_handover_of_work_network(log: Union[EventLog, pd.DataFrame], beta=0):
    """
    Calculates the handover of work network of the event log.
    The handover of work network is essentially the DFG of the event log, however, using the
    resource as a node of the graph, instead of the activity.
    As such, to use this, resource information should be present in the event log.

    Parameters
    ---------------
    log
        Event log or Pandas dataframe
    beta
        beta parameter for Handover metric

    Returns
    ---------------
    metric_values
        Values of the metric
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    from pm4py.algo.organizational_mining.sna import algorithm as sna
    parameters = get_properties(log)
    parameters["beta"] = beta
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        return sna.apply(log, variant=sna.Variants.HANDOVER_PANDAS, parameters=parameters)
    else:
        return sna.apply(log, variant=sna.Variants.HANDOVER_LOG, parameters=parameters)


def discover_working_together_network(log: Union[EventLog, pd.DataFrame]):
    """
    Calculates the working together network of the process.
    Two nodes resources are connected in the graph if the resources collaborate on an instance of the process.

    Parameters
    ---------------
    log
        Event log or Pandas dataframe

    Returns
    ---------------
    metric_values
        Values of the metric
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    from pm4py.algo.organizational_mining.sna import algorithm as sna
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        return sna.apply(log, variant=sna.Variants.WORKING_TOGETHER_PANDAS, parameters=get_properties(log))
    else:
        return sna.apply(log, variant=sna.Variants.WORKING_TOGETHER_LOG, parameters=get_properties(log))


def discover_activity_based_resource_similarity(log: Union[EventLog, pd.DataFrame]):
    """
    Calculates similarity between the resources in the event log, based on their activity profiles.

    Parameters
    ---------------
    log
        Event log or Pandas dataframe

    Returns
    ---------------
    metric_values
        Values of the metric
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    from pm4py.algo.organizational_mining.sna import algorithm as sna
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        return sna.apply(log, variant=sna.Variants.JOINTACTIVITIES_PANDAS, parameters=get_properties(log))
    else:
        return sna.apply(log, variant=sna.Variants.JOINTACTIVITIES_LOG, parameters=get_properties(log))


def discover_subcontracting_network(log: Union[EventLog, pd.DataFrame], n=2):
    """
    Calculates the subcontracting network of the process.

    Parameters
    ---------------
    log
        Event log or Pandas dataframe
    n
        n parameter for Subcontracting metric

    Returns
    ---------------
    metric_values
        Values of the metric
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    from pm4py.algo.organizational_mining.sna import algorithm as sna
    parameters = get_properties(log)
    parameters["n"] = n
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        return sna.apply(log, variant=sna.Variants.SUBCONTRACTING_PANDAS, parameters=parameters)
    else:
        return sna.apply(log, variant=sna.Variants.SUBCONTRACTING_LOG, parameters=parameters)


def discover_organizational_roles(log: Union[EventLog, pd.DataFrame]):
    """
    Mines the organizational roles

    Parameters
    ---------------
    log
        Event log or Pandas dataframe

    Returns
    ---------------
    roles
        Organizational roles. List where each role is a sublist with two elements:
        - The first element of the sublist is the list of activities belonging to a role.
        Each activity belongs to a single role
        - The second element of the sublist is a dictionary containing the resources of the role
        and the number of times they executed activities belonging to the role.
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    from pm4py.algo.organizational_mining.roles import algorithm as roles
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        return roles.apply(log, variant=roles.Variants.PANDAS, parameters=get_properties(log))
    else:
        return roles.apply(log, variant=roles.Variants.LOG, parameters=get_properties(log))


def discover_network_analysis(log: Union[pd.DataFrame, EventLog, EventStream], out_column: str, in_column: str, node_column_source: str, node_column_target: str, edge_column: str, edge_reference: str = "_out", performance: bool = False, sorting_column: str = xes_constants.DEFAULT_TIMESTAMP_KEY, timestamp_column: str = xes_constants.DEFAULT_TIMESTAMP_KEY) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """
    Performs a network analysis of the log based on the provided parameters.
    The output is a multigraph.
    Two events EV1 and EV2 of the log are merged (indipendently from the case notion) based on having
    EV1.OUT_COLUMN = EV2.IN_COLUMN.
    Then, an aggregation is applied on the couple of events (NODE_COLUMN) to obtain the nodes that are connected.
    The edges between these nodes are aggregated based on some property of the *source* event (EDGE_COLUMN).

    Parameters
    ------------------
    log
        Event log / Pandas dataframe
    out_column
        The source column of the link (default: the case identifier; events of the same case are linked)
    in_column
        The target column of the link (default: the case identifier; events of the same case are linked)
    node_column_source
        The attribute to be used for the node definition of the source event (default: the resource of the log, org:resource)
    node_column_target
        The attribute to be used for the node definition of the target event (default: the resource of the log, org:resource)
    edge_column
        The attribute to be used for the edge definition (default: the activity of the log,
            concept:name)
    edge_reference
        Decide if the edge attribute should be picked from the source event. Values:
                - _out  =>  the source event
                - _in   =>  the target event
    performance
        Boolean value that enables the performance calculation on the edges of the network analysis
    sorting_column
        The column that should be used to sort the log before performing the network analysis (default: time:timestamp)
    timestamp_column
        The column that should be used as timestamp for the performance-related analysis (default: time:timestamp)

    Returns
    ------------------
    network_analysis
        Edges of the network analysis (first key: edge; second key: type; value: number of occurrences)
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")


    from pm4py.algo.organizational_mining.network_analysis.variants import dataframe
    parameters = {}
    parameters[dataframe.Parameters.OUT_COLUMN] = out_column
    parameters[dataframe.Parameters.IN_COLUMN] = in_column
    parameters[dataframe.Parameters.NODE_COLUMN_SOURCE] = node_column_source
    parameters[dataframe.Parameters.NODE_COLUMN_TARGET] = node_column_target
    parameters[dataframe.Parameters.EDGE_COLUMN] = edge_column
    parameters[dataframe.Parameters.EDGE_REFERENCE] = edge_reference
    parameters[dataframe.Parameters.SORTING_COLUMN] = sorting_column
    parameters[dataframe.Parameters.TIMESTAMP_KEY] = timestamp_column
    parameters[dataframe.Parameters.INCLUDE_PERFORMANCE] = performance

    from pm4py.algo.organizational_mining.network_analysis import algorithm as network_analysis
    return network_analysis.apply(log, parameters=parameters)
