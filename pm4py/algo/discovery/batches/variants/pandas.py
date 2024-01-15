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
from typing import Optional, Dict, Any, List, Tuple, Union

import pandas as pd

from pm4py.algo.discovery.batches.utils import detection
from pm4py.util import exec_utils, constants, xes_constants, pandas_utils
import numpy as np


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    EVENT_ID_KEY = "event_id_key"
    MERGE_DISTANCE = "merge_distance"
    MIN_BATCH_SIZE = "min_batch_size"


def apply(log: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> List[
    Tuple[Tuple[str, str], int, Dict[str, Any]]]:
    """
    Provided a Pandas dataframe, returns
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
        Dataframe
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

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes_constants.DEFAULT_RESOURCE_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     timestamp_key)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    event_id_key = exec_utils.get_param_value(Parameters.EVENT_ID_KEY, parameters, constants.DEFAULT_INDEX_KEY)

    attributes_to_consider = {activity_key, resource_key, start_timestamp_key, timestamp_key, case_id_key}
    log_contains_evidkey = event_id_key in log
    if log_contains_evidkey:
        attributes_to_consider.add(event_id_key)

    log = log[list(attributes_to_consider)]
    # the timestamp columns are expressed in nanoseconds values
    # here, we want them to have the second granularity, so we divide by 10**9
    # for example 1001000000 nanoseconds (value stored in the column)
    # is equivalent to 1,001 seconds.
    log[timestamp_key] = pandas_utils.convert_to_seconds(log[timestamp_key])
    if start_timestamp_key != timestamp_key:
        # see the aforementioned explanation.
        log[start_timestamp_key] = pandas_utils.convert_to_seconds(log[start_timestamp_key])

    actres_grouping0 = log.groupby([activity_key, resource_key]).agg(list).to_dict()
    start_timestamps = actres_grouping0[start_timestamp_key]
    complete_timestamps = actres_grouping0[timestamp_key]
    cases = actres_grouping0[case_id_key]
    if log_contains_evidkey:
        events_ids = actres_grouping0[event_id_key]

    actres_grouping = {}
    for k in start_timestamps:
        st = start_timestamps[k]
        et = complete_timestamps[k]
        c = cases[k]
        if log_contains_evidkey:
            eid = events_ids[k]
        actres_grouping_k = []
        for i in range(len(st)):
            if log_contains_evidkey:
                actres_grouping_k.append((st[i], et[i], c[i], eid[i]))
            else:
                actres_grouping_k.append((st[i], et[i], c[i]))
        actres_grouping[k] = actres_grouping_k

    return detection.detect(actres_grouping, parameters=parameters)
