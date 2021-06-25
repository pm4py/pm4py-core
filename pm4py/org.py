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

from pm4py.objects.log.obj import EventLog
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties


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
    from pm4py.algo.organizational_mining.roles import algorithm as roles
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        return roles.apply(log, variant=roles.Variants.PANDAS, parameters=get_properties(log))
    else:
        return roles.apply(log, variant=roles.Variants.LOG, parameters=get_properties(log))
