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
__doc__ = """
The ``pm4py.org`` module contains the organizational analysis techniques offered in ``pm4py``
"""

from typing import Union

import pandas as pd

from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties, __event_log_deprecation_warning
from pm4py.objects.org.sna.obj import SNA
from pm4py.objects.org.roles.obj import Role
from pm4py.util import xes_constants
from typing import Dict, Tuple, Any, List


def discover_handover_of_work_network(log: Union[EventLog, pd.DataFrame], beta=0, resource_key: str = "org:resource", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> SNA:
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

    .. code-block:: python3

        import pm4py

        metric = pm4py.discover_handover_of_work_network(dataframe, resource_key='org:resource', timestamp_key='time:timestamp', case_id_key='case:concept:name')
    """
    __event_log_deprecation_warning(log)

    from pm4py.algo.organizational_mining.sna import algorithm as sna
    parameters = get_properties(log, resource_key=resource_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["beta"] = beta
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, timestamp_key=timestamp_key, case_id_key=case_id_key)
        return sna.apply(log, variant=sna.Variants.HANDOVER_PANDAS, parameters=parameters)
    else:
        return sna.apply(log, variant=sna.Variants.HANDOVER_LOG, parameters=parameters)


def discover_working_together_network(log: Union[EventLog, pd.DataFrame], resource_key: str = "org:resource", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> SNA:
    """
    Calculates the working together network of the process.
    Two nodes resources are connected in the graph if the resources collaborate on an instance of the process.

    :param log: event log / Pandas dataframe
    :param resource_key: attribute to be used for the resource
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier

    .. code-block:: python3

        import pm4py

        metric = pm4py.discover_working_together_network(dataframe, resource_key='org:resource', timestamp_key='time:timestamp', case_id_key='case:concept:name')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, resource_key=resource_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.organizational_mining.sna import algorithm as sna
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, timestamp_key=timestamp_key, case_id_key=case_id_key)
        return sna.apply(log, variant=sna.Variants.WORKING_TOGETHER_PANDAS, parameters=properties)
    else:
        return sna.apply(log, variant=sna.Variants.WORKING_TOGETHER_LOG, parameters=properties)


def discover_activity_based_resource_similarity(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", resource_key: str = "org:resource", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> SNA:
    """
    Calculates similarity between the resources in the event log, based on their activity profiles.

    :param log: event log / Pandas dataframe
    :param activity_key: attribute to be used for the activity
    :param resource_key: attribute to be used for the resource
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier

    .. code-block:: python3

        import pm4py

        act_res_sim = pm4py.discover_activity_based_resource_similarity(dataframe, resource_key='org:resource', activity_key='concept:name', timestamp_key='time:timestamp', case_id_key='case:concept:name')
    """
    __event_log_deprecation_warning(log)

    properties = get_properties(log, activity_key=activity_key, resource_key=resource_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.organizational_mining.sna import algorithm as sna
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
        return sna.apply(log, variant=sna.Variants.JOINTACTIVITIES_PANDAS, parameters=properties)
    else:
        return sna.apply(log, variant=sna.Variants.JOINTACTIVITIES_LOG, parameters=properties)


def discover_subcontracting_network(log: Union[EventLog, pd.DataFrame], n=2, resource_key: str = "org:resource", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> SNA:
    """
    Calculates the subcontracting network of the process.

    :param log: event log / Pandas dataframe
    :param n: n parameter for Subcontracting metric
    :param resource_key: attribute to be used for the resource
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier

    .. code-block:: python3

        import pm4py

        metric = pm4py.discover_subcontracting_network(dataframe, resource_key='org:resource', timestamp_key='time:timestamp', case_id_key='case:concept:name')
    """
    __event_log_deprecation_warning(log)

    from pm4py.algo.organizational_mining.sna import algorithm as sna
    parameters = get_properties(log, resource_key=resource_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["n"] = n
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, timestamp_key=timestamp_key, case_id_key=case_id_key)
        return sna.apply(log, variant=sna.Variants.SUBCONTRACTING_PANDAS, parameters=parameters)
    else:
        return sna.apply(log, variant=sna.Variants.SUBCONTRACTING_LOG, parameters=parameters)


def discover_organizational_roles(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", resource_key: str = "org:resource", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> List[Role]:
    """
    Mines the organizational roles

    A role is a set of activities in the log that are executed by a similar (multi)set of resources. Hence, it is a specific function into organization. Grouping the activities in roles can help:

    Reference paper:
    Burattin, Andrea, Alessandro Sperduti, and Marco Veluscek. “Business models enhancement through discovery of roles.” 2013 IEEE Symposium on Computational Intelligence and Data Mining (CIDM). IEEE, 2013.

    :param log: event log / Pandas dataframe
    :param activity_key: attribute to be used for the activity
    :param resource_key: attribute to be used for the resource
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier

    .. code-block:: python3

        import pm4py

        roles = pm4py.discover_organizational_roles(dataframe, resource_key='org:resource', activity_key='concept:name', timestamp_key='time:timestamp', case_id_key='case:concept:name')
    """
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

    The classical social network analysis methods are based on the order of the events inside a case. For example, the Handover of Work metric considers the directly-follows relationships between resources during the work of a case. An edge is added between the two resources if such relationships occurs.

    Real-life scenarios may be more complicated. At first, is difficult to collect events inside the same case without having convergence/divergence issues (see first section of the OCEL part). At second, the type of relationship may also be important. Consider for example the relationship between two resources: this may be more efficient if the activity that is executed is liked by the resources, rather than disgusted.

    The network analysis that we introduce here generalizes some existing social network analysis metrics, becoming independent from the choice of a case notion and permitting to build a multi-graph instead of a simple graph.

    With this, we assume events to be linked by signals. An event emits a signal (that is contained as one attribute of the event) that is assumed to be received by other events (also, this is an attribute of these events) that follow the first event in the log. So, we assume there is an OUT attribute (of the event) that is identical to the IN attribute (of the other events).

    When we collect this information, we can build the network analysis graph:
    - The source node of the relation is given by an aggregation over a node_column_source attribute.
    - The target node of the relation is given by an aggregation over a node_column_target attribute.
    - The type of edge is given by an aggregation over an edge_column attribute.
    - The network analysis graph can either be annotated with frequency or performance information.

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

    .. code-block:: python3

        import pm4py

        net_ana = pm4py.discover_network_analysis(dataframe, out_column='case:concept:name', in_column='case:concept:name', node_column_source='org:resource', node_column_target='org:resource', edge_column='concept:name')
    """
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
