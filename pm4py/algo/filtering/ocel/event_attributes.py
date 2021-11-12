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
from pm4py.util import exec_utils, constants
from pm4py.objects.ocel.util import filtering_utils
from copy import copy
from typing import Dict, Any, Optional, Collection, Union
from pm4py.algo.filtering.common.timestamp.timestamp_common import get_dt_from_string
from pm4py.objects.ocel.obj import OCEL
import datetime


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    POSITIVE = "positive"


def apply(ocel: OCEL, values: Collection[Any], parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Filters the object-centric event log on the provided event attributes values

    Parameters
    ----------------
    ocel
        Object-centric event log
    values
        Collection of values
    parameters
        Parameters of the algorithm, including:
        - Parameters.ATTRIBUTE_KEY => the attribute that should be filtered
        - Parameters.POSITIVE => decides if the values should be kept (positive=True) or removed (positive=False)

    Returns
    ----------------
    ocel
        Filtered object-centric event log
    """
    if parameters is None:
        parameters = {}

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, ocel.event_activity)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    ocel = copy(ocel)
    if positive:
        ocel.events = ocel.events[ocel.events[attribute_key].isin(values)]
    else:
        ocel.events = ocel.events[~ocel.events[attribute_key].isin(values)]

    return filtering_utils.propagate_event_filtering(ocel, parameters=parameters)


def apply_timestamp(ocel: OCEL, min_timest: Union[datetime.datetime, str], max_timest: Union[datetime.datetime, str], parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Filters the object-centric event log keeping events in the provided timestamp range

    Parameters
    -----------------
    ocel
        Object-centric event log
    min_timest
        Left extreme of the allowed timestamp interval (provided in the format: YYYY-mm-dd HH:MM:SS)
    max_timest
        Right extreme of the allowed timestamp interval (provided in the format: YYYY-mm-dd HH:MM:SS)
    parameters
        Parameters of the algorithm, including:
        - Parameters.TIMESTAMP_KEY => the attribute to use as timestamp

    Returns
    -----------------
    filtered_ocel
        Filtered object-centric event log
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, ocel.event_timestamp)
    min_timest = get_dt_from_string(min_timest)
    max_timest = get_dt_from_string(max_timest)

    ocel = copy(ocel)
    ocel.events = ocel.events[ocel.events[timestamp_key] >= min_timest]
    ocel.events = ocel.events[ocel.events[timestamp_key] <= max_timest]

    return filtering_utils.propagate_event_filtering(ocel, parameters=parameters)
