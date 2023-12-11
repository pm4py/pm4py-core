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
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any, Tuple, Collection, Set, List
from enum import Enum
from pm4py.util import exec_utils, constants
from pm4py.objects.ocel import constants as ocel_constants
from pm4py.util.business_hours import BusinessHours
import numpy as np
import datetime


class Parameters(Enum):
    EVENT_ID = ocel_constants.PARAM_EVENT_ID
    OBJECT_ID = ocel_constants.PARAM_OBJECT_ID
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE
    EVENT_ACTIVITY = ocel_constants.PARAM_EVENT_ACTIVITY
    EVENT_TIMESTAMP = ocel_constants.PARAM_EVENT_TIMESTAMP
    BUSINESS_HOURS = "business_hours"
    BUSINESS_HOUR_SLOTS = "business_hour_slots"
    WORKCALENDAR = "workcalendar"


def performance_calculation_ocel_aggregation(ocel: OCEL, aggregation: Dict[str, Dict[Tuple[str, str], Set[Any]]],
                                             parameters: Optional[Dict[Any, Any]] = None) -> Dict[
    str, Dict[Tuple[str, str], List[float]]]:
    """
    Calculates the performance based on one of the following aggregations:
    - aggregate_ev_couples
    - aggregate_total_objects

    Parameters
    ----------------
    ocel
        Object-centric event log
    aggregation
        Aggregation calculated using one of the aforementioned methods
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID => the event identifier
        - Parameters.EVENT_TIMESTAMP => the timestamp
        - Parameters.BUSINESS_HOURS => enables/disables the business hours
        - Parameters.BUSINESS_HOURS_SLOTS =>
        work schedule of the company, provided as a list of tuples where each tuple represents one time slot of business
        hours. One slot i.e. one tuple consists of one start and one end time given in seconds since week start, e.g.
        [
            (7 * 60 * 60, 17 * 60 * 60),
            ((24 + 7) * 60 * 60, (24 + 12) * 60 * 60),
            ((24 + 13) * 60 * 60, (24 + 17) * 60 * 60),
        ]
        meaning that business hours are Mondays 07:00 - 17:00 and Tuesdays 07:00 - 12:00 and 13:00 - 17:00

    Returns
    ----------------
    edges_performance
        For each object type, associate a dictionary where to each activity couple
        all the times between the activities are recorded.
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    timestamp_key = exec_utils.get_param_value(Parameters.EVENT_TIMESTAMP, parameters, ocel.event_timestamp)
    timestamps = ocel.events.groupby(event_id)[timestamp_key].agg(list).to_dict()
    timestamps = {x: y[0] for x, y in timestamps.items()}

    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    business_hours_slots = exec_utils.get_param_value(Parameters.BUSINESS_HOUR_SLOTS, parameters, constants.DEFAULT_BUSINESS_HOUR_SLOTS)

    workcalendar = exec_utils.get_param_value(Parameters.WORKCALENDAR, parameters, constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR)

    ret = {}

    for ot in aggregation:
        ret[ot] = {}
        for act in aggregation[ot]:
            ret[ot][act] = []
            for el in aggregation[ot][act]:
                if business_hours:
                    bh = BusinessHours(timestamps[el[0]],
                                       timestamps[el[1]],
                                       business_hour_slots=business_hours_slots,
                                       workcalendar=workcalendar)
                    diff = bh.get_seconds()
                else:
                    timedelta = timestamps[el[1]] - timestamps[el[0]]
                    diff = 0
                    if isinstance(timedelta, np.timedelta64):
                        diff = timedelta / np.timedelta64(1, 's')
                    elif isinstance(timedelta, datetime.timedelta):
                        diff = timedelta.total_seconds()
                ret[ot][act].append(diff)
            ret[ot][act] = sorted(ret[ot][act])

    return ret


def aggregate_ev_couples(edges: Dict[str, Dict[Tuple[str, str], Collection[Any]]]) -> Dict[
    str, Dict[Tuple[str, str], Set[Any]]]:
    """
    Performs an aggregation of the occurrences of a given edge on the couple of events (source event, target event).

    Parameters
    -------------------
    edges
        Edges calculated using the find_associations_per_edge function

    Returns
    -------------------
    aggregation
        A dictionary associating to each object type another dictionary where to each edge (activity couple) all the
        couples of related events are associated.
    """
    ret = {}
    for ot in edges:
        ret[ot] = {}
        for act in edges[ot]:
            ret[ot][act] = set((x[0], x[1]) for x in edges[ot][act])
    return ret


def aggregate_unique_objects(edges: Dict[str, Dict[Tuple[str, str], Collection[Any]]]) -> Dict[
    str, Dict[Tuple[str, str], Set[Any]]]:
    """
    Performs an aggregation of the occurrences of a given edge in the involved object.

    Parameters
    -------------------
    edges
        Edges calculated using the find_associations_per_edge function

    Returns
    -------------------
    aggregation
        A dictionary associating to each object type another dictionary where to each edge (activity couple) all the
        involved objects are associated.
    """
    ret = {}
    for ot in edges:
        ret[ot] = {}
        for act in edges[ot]:
            ret[ot][act] = set(x[2] for x in edges[ot][act])
    return ret


def aggregate_total_objects(edges: Dict[str, Dict[Tuple[str, str], Collection[Any]]]) -> Dict[
    str, Dict[Tuple[str, str], Set[Any]]]:
    """
    Performs an aggregation of the occurrences of a given edge on the triple (source event, target event, object).

    Parameters
    -------------------
    edges
        Edges calculated using the find_associations_per_edge function

    Returns
    -------------------
    aggregation
        A dictionary associating to each object type another dictionary where to each edge (activity couple) all the
        triples (source event, target event, object) are associated.
    """
    ret = {}
    for ot in edges:
        ret[ot] = {}
        for act in edges[ot]:
            ret[ot][act] = set(edges[ot][act])
    return ret


def find_associations_per_edge(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[
    str, Dict[Tuple[str, str], Collection[Any]]]:
    """
    Finds all the occurrences of a given edge (activity couple), expressed as triples (source event, target event, object ID).

    Parameters
    -------------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ACTIVITY => the activity
        - Parameters.EVENT_ID => the event identifier
        - Parameters.OBJECT_ID => the object identifier
        - Parameters.OBJECT_TYPE => the object type

    Returns
    ------------------
    edges
        A dictionary associating to each object type a dictionary where to each edge (activity couple) the list of triples (source event, target event, object ID)
        is associated.
    """
    if parameters is None:
        parameters = {}

    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters, ocel.event_activity)
    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel.object_id_column)
    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)

    identifiers = ocel.events[event_id].to_numpy().tolist()
    activities = ocel.events.groupby(event_id)[event_activity].agg(list).to_dict()
    activities = {x: y[0] for x, y in activities.items()}

    omap = ocel.relations.groupby(event_id)[object_id].agg(list).to_dict()
    objtypes = ocel.objects.groupby(object_id)[object_type].agg(list).to_dict()
    objtypes = {x: y[0] for x, y in objtypes.items()}

    history = {}
    edges = {}

    for evid in identifiers:
        if evid in omap:
            for obj in omap[evid]:
                if obj in history:
                    objtype = objtypes[obj]
                    if objtype not in edges:
                        edges[objtype] = {}
                    previd = history[obj]
                    acttup = (activities[previd], activities[evid])
                    if acttup not in edges[objtype]:
                        edges[objtype][acttup] = list()
                    edges[objtype][acttup].append((previd, evid, obj))
                history[obj] = evid

    return edges
