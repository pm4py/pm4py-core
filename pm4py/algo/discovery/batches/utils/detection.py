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
from typing import Tuple, List, Any, Set, Optional, Dict, Union

from pm4py.util import exec_utils
import heapq
from copy import copy


class Parameters(Enum):
    MERGE_DISTANCE = "merge_distance"
    MIN_BATCH_SIZE = "min_batch_size"


class BatchType(Enum):
    SIMULTANEOUS = "Simultaneous"
    BATCHING_START = "Batching on Start"
    BATCHING_END = "Batching on End"
    SEQ_BATCHING = "Sequential batching"
    CONC_BATCHING = "Concurrent batching"


def __merge_overlapping_intervals(intervals: List[Tuple[float, float, Set[Any]]]) -> List[Tuple[float, float, Set[Any]]]:
    """
    Iterative method that merges the overlapping time intervals
    (an interval [a, b] is overlapping to [c, d] if a <= c <= b or c <= a <= d).
    """
    continue_cycle = True
    while continue_cycle:
        continue_cycle = False
        i = 0
        while i < len(intervals) - 1:
            if intervals[i][1] > intervals[i + 1][0]:
                # decide to merge interval i and i+1
                new_interval = (min(intervals[i][0], intervals[i + 1][0]), max(intervals[i][1], intervals[i + 1][1]),
                                intervals[i][2].union(intervals[i + 1][2]))
                # add the new interval to the list
                intervals.append(new_interval)
                # remove the i+1 interval
                del intervals[i + 1]
                # remove the i interval
                del intervals[i]
                # sort the intervals
                intervals.sort()
                # set the variable continue_cycle to True
                continue_cycle = True
                # interrupt the current iteration on the intervals
                break
            i = i + 1
    return intervals


def __merge_near_intervals(intervals: List[Tuple[float, float, Set[Any]]], max_allowed_distance: float) -> List[
    Tuple[float, float, Set[Any]]]:
    """
    Merge the non-overlapping time intervals that are nearer than max_allowed_distance.
    (an interval [a, b] that is non-overlapping with [c, d] having b < c, is merged if c - b <= max_allowed_distance).
    """
    continue_cycle = True
    while continue_cycle:
        continue_cycle = False
        i = 0
        while i < len(intervals) - 1:
            if intervals[i + 1][0] - intervals[i][1] <= max_allowed_distance:
                # decide to merge interval i and i+1
                new_interval = (min(intervals[i][0], intervals[i + 1][0]), max(intervals[i][1], intervals[i + 1][1]),
                                intervals[i][2].union(intervals[i + 1][2]))
                # remove the i+1 interval
                del intervals[i + 1]
                # remove the i interval
                del intervals[i]
                # add the new interval to the list
                heapq.heappush(intervals, new_interval)
                # set the variable continue_cycle to True
                continue_cycle = True
                i = i - 1
            i = i + 1
    return intervals


def __check_batch_type(batch: Tuple[float, float, Set[Any]]) -> str:
    """
    Checks the batch type between:
    - Simultaneous (all the events in the batch have identical start and end timestamps)
    - Batching at start (all the events in the batch have identical start timestamp)
    - Batching at end (all the events in the batch have identical end timestamp)
    - Sequential batching (for all the consecutive events, the end of the first is equal to the start of the second)
    - Concurrent batching (for all the consecutive events that are not sequentially matched)
    """
    events_batch = sorted(list(batch[2]))
    # take the minimum of the left-extreme of each interval
    min_left_events = min(ev[0] for ev in events_batch)
    # take the maximum of the left-extreme of each interval
    max_left_events = max(ev[0] for ev in events_batch)
    # take the minimum of the right-extreme of each interval
    min_right_events = min(ev[1] for ev in events_batch)
    # take the maximum of the right-extreme of each interval
    max_right_events = max(ev[1] for ev in events_batch)

    # CONDITION 1 - All the events in the batch have identical start and end timestamps
    if min_left_events == max_left_events and min_right_events == max_right_events:
        return BatchType.SIMULTANEOUS.value
    # CONDITION 4 - All the events in the batch have identical start timestamp:
    if min_left_events == max_left_events:
        return BatchType.BATCHING_START.value
    # CONDITION 5 - All the events in the batch have identical end timestamp:
    if min_right_events == max_right_events:
        return BatchType.BATCHING_END.value

    # now we could be in the SEQUENTIAL batching or the CONCURRENT batching
    # in order to be in the SEQUENTIAL, we need that for all the consecutive events the end of the first is equal to the start of the second
    is_sequential = True
    i = 0
    while i < len(events_batch) - 1:
        # if there are two consecutive events that are not sequentially matched, then we automatically fall inside the CONCURRENT batching
        if events_batch[i][1] != events_batch[i + 1][0]:
            is_sequential = False
            break
        i = i + 1
    if is_sequential:
        return BatchType.SEQ_BATCHING.value
    else:
        return BatchType.CONC_BATCHING.value


def __detect_single(events: List[Tuple[float, float, str]], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[
    str, List[Any]]:
    """
    Detect if there are batches in the execution of events having a given activity-resource combination
    """
    if parameters is None:
        parameters = {}

    ret = {BatchType.SIMULTANEOUS.value: [], BatchType.BATCHING_START.value: [], BatchType.BATCHING_END.value: [],
           BatchType.CONC_BATCHING.value: [], BatchType.SEQ_BATCHING.value: []}
    merge_distance = exec_utils.get_param_value(Parameters.MERGE_DISTANCE, parameters, 15 * 60)
    min_batch_size = exec_utils.get_param_value(Parameters.MIN_BATCH_SIZE, parameters, 2)

    intervals = [(e[0], e[1], {copy(e)}) for e in
                 events]
    heapq.heapify(intervals)
    intervals = __merge_overlapping_intervals(intervals)
    intervals = __merge_near_intervals(intervals, merge_distance)
    batches = [x for x in intervals if len(x[2]) >= min_batch_size]
    for batch in batches:
        batch_type = __check_batch_type(batch)
        ret[batch_type].append(batch)
    ret = {x: y for x, y in ret.items() if y}
    return ret


def detect(actres_grouping: Dict[Tuple[str, str], List[Tuple[float, float, str]]],
           parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> List[Tuple[Tuple[str, str], int, Dict[str, Any]]]:
    """
    Provided an activity-resource grouping of the events of the event log, returns
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
    actres_grouping
        Activity-resource grouping of events
    parameters
        Parameters of the algorithm

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
    ret = []
    for actres in actres_grouping:
        batches = __detect_single(actres_grouping[actres], parameters=parameters)
        if batches:
            total_length = sum(len(y) for y in batches.values())
            ret.append((actres, total_length, batches))
    ret = sorted(ret, reverse=True, key=lambda x: (x[1], x[0]))
    return ret
