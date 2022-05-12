__doc__ = """
"""

from typing import Union, Optional

import pandas as pd

from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties, __event_log_deprecation_warning
from pm4py.util import constants, xes_constants
from typing import Dict, Tuple, Any


def discover_handover_of_work_network(log: Union[EventLog, pd.DataFrame], beta=0, resource_key: str = "org:resource", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name"):
    """
    Calculates the handover of work network of the event log.
    The handover of work network is essentially the DFG of the event log, however, using the
    resource as a node of the graph, instead of the activity.
    As such, to use this, resource information should be present in the event log.

    :param log: event log / Pandas dataframe
    :param beta: beta parameter for Handover metric
    :param resource_key: attribute to be used for the resource
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.algo.organizational_mining.sna import algorithm as sna
    parameters = get_properties(log, resource_key=resource_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["beta"] = beta
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, timestamp_key=timestamp_key, case_id_key=case_id_key)
        return sna.apply(log, variant=sna.Variants.HANDOVER_PANDAS, parameters=parameters)
    else:
        return sna.apply(log, variant=sna.Variants.HANDOVER_LOG, parameters=parameters)


def discover_working_together_network(log: Union[EventLog, pd.DataFrame], resource_key: str = "org:resource", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name"):
    """
    Calculates the working together network of the process.
    Two nodes resources are connected in the graph if the resources collaborate on an instance of the process.

    :param log: event log / Pandas dataframe
    :param resource_key: attribute to be used for the resource
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, resource_key=resource_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.organizational_mining.sna import algorithm as sna
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, timestamp_key=timestamp_key, case_id_key=case_id_key)
        return sna.apply(log, variant=sna.Variants.WORKING_TOGETHER_PANDAS, parameters=properties)
    else:
        return sna.apply(log, variant=sna.Variants.WORKING_TOGETHER_LOG, parameters=properties)


def discover_activity_based_resource_similarity(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", resource_key: str = "org:resource", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name"):
    """
    Calculates similarity between the resources in the event log, based on their activity profiles.

    :param log: event log / Pandas dataframe
    :param activity_key: attribute to be used for the activity
    :param resource_key: attribute to be used for the resource
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, resource_key=resource_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.organizational_mining.sna import algorithm as sna
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        return sna.apply(log, variant=sna.Variants.JOINTACTIVITIES_PANDAS, parameters=properties)
    else:
        return sna.apply(log, variant=sna.Variants.JOINTACTIVITIES_LOG, parameters=properties)


def discover_subcontracting_network(log: Union[EventLog, pd.DataFrame], n=2, resource_key: str = "org:resource", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name"):
    """
    Calculates the subcontracting network of the process.

    :param log: event log / Pandas dataframe
    :param n: n parameter for Subcontracting metric
    :param resource_key: attribute to be used for the resource
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.algo.organizational_mining.sna import algorithm as sna
    parameters = get_properties(log, resource_key=resource_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["n"] = n
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, timestamp_key=timestamp_key, case_id_key=case_id_key)
        return sna.apply(log, variant=sna.Variants.SUBCONTRACTING_PANDAS, parameters=parameters)
    else:
        return sna.apply(log, variant=sna.Variants.SUBCONTRACTING_LOG, parameters=parameters)


def discover_organizational_roles(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", resource_key: str = "org:resource", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name"):
    """
    Mines the organizational roles

    :param log: event log / Pandas dataframe
    :param activity_key: attribute to be used for the activity
    :param resource_key: attribute to be used for the resource
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, resource_key=resource_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.organizational_mining.roles import algorithm as roles
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        return roles.apply(log, variant=roles.Variants.PANDAS, parameters=properties)
    else:
        return roles.apply(log, variant=roles.Variants.LOG, parameters=properties)


def discover_network_analysis(log: Union[pd.DataFrame, EventLog, EventStream], out_column: str, in_column: str, node_column_source: str, node_column_target: str, edge_column: str, edge_reference: str = "_out", performance: bool = False, sorting_column: str = xes_constants.DEFAULT_TIMESTAMP_KEY, timestamp_column: str = xes_constants.DEFAULT_TIMESTAMP_KEY) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """
    Performs a network analysis of the log based on the provided parameters.
    The output is a multigraph.
    Two events EV1 and EV2 of the log are merged (indipendently from the case notion) based on having
    EV1.OUT_COLUMN = EV2.IN_COLUMN.
    Then, an aggregation is applied on the couple of events (NODE_COLUMN) to obtain the nodes that are connected.
    The edges between these nodes are aggregated based on some property of the *source* event (EDGE_COLUMN).

    :param log: event log / Pandas dataframe
    :param out_column: the source column of the link (default: the case identifier; events of the same case are linked)
    :param in_column: the target column of the link (default: the case identifier; events of the same case are linked)
    :param node_column_source: the attribute to be used for the node definition of the source event (default: the resource of the log, org:resource)
    :param node_column_target: the attribute to be used for the node definition of the target event (default: the resource of the log, org:resource)
    :param edge_column: the attribute to be used for the edge definition (default: the activity of the log, concept:name)
    :param edge_reference: decide if the edge attribute should be picked from the source event. Values: _out  =>  the source event ; _in   =>  the target event
    :param performance: boolean value that enables the performance calculation on the edges of the network analysis
    :param sorting_column: the column that should be used to sort the log before performing the network analysis (default: time:timestamp)
    :param timestamp_column: the column that should be used as timestamp for the performance-related analysis (default: time:timestamp)
    :rtype: ``Dict[Tuple[str, str], Dict[str, Any]]``
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)

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
