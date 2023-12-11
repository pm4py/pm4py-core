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
from typing import Union, Optional, Dict, Any, List, Tuple

import pandas as pd

from pm4py.algo.discovery.batches.variants import pandas, log
from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils, pandas_utils


class Variants(Enum):
    LOG = log
    PANDAS = pandas


def apply(log: Union[EventLog, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> List[
    Tuple[Tuple[str, str], int, Dict[str, Any]]]:
    """
    Provided an event log / dataframe, returns
    a list having as elements the activity-resources with the batches that are detected, divided in:
    - Simultaneous (all the events in the batch have identical start and end timestamps)
    - Batching at start (all the events in the batch have identical start timestamp)
    - Batching at end (all the events in the batch have identical end timestamp)
    - Sequential batching (for all the consecutive events, the end of the first is equal to the start of the second)
    - Concurrent batching (for all the consecutive events that are not sequentially matched)

    The approach has been described in the following paper:
    Martin, N., Swennen, M., Depaire, B., Jans, M., Caris, A., & Vanhoof, K. (2015, December). Batch Processing:
    Definition and Event Log Identification. In SIMPDA (pp. 137-140).

    Parameters
    -------------------
    log
        Event log / dataframe object
    parameters
        Parameters of the algorithm:
        - ACTIVITY_KEY => the attribute that should be used as activity
        - RESOURCE_KEY => the attribute that should be used as resource
        - START_TIMESTAMP_KEY => the attribute that should be used as start timestamp
        - TIMESTAMP_KEY => the attribute that should be used as timestamp
        - CASE_ID_KEY => the attribute that should be used as case identifier
        - MERGE_DISTANCE => the maximum time distance between non-overlapping intervals in order for them to be
            considered belonging to the same batch (default: 15*60   15 minutes)
        - MIN_BATCH_SIZE => the minimum number of events for a batch to be considered (default: 2)

    Returns
    ------------------
    list_batches
        A (sorted) list containing tuples. Each tuple contain:
        - Index 0: the activity-resource for which at least one batch has been detected
        - Index 1: the number of batches for the given activity-resource
        - Index 2: a list containing all the batches. Each batch is described by:
            # The start timestamp of the batch
            # The complete timestamp of the batch
            # The list of events that are executed in the batch
    """
    if parameters is None:
        parameters = {}

    if pandas_utils.check_is_pandas_dataframe(log):
        return exec_utils.get_variant(Variants.PANDAS).apply(log, parameters=parameters)
    else:
        return exec_utils.get_variant(Variants.LOG).apply(log, parameters=parameters)
