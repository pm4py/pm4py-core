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
from typing import Optional, Dict, Any

import pandas as pd

from pm4py.objects.ocel import constants as ocel_constants
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import constants, xes_constants
from pm4py.util import exec_utils


class Parameters(Enum):
    EVENT_ACTIVITY = ocel_constants.PARAM_EVENT_ACTIVITY
    EVENT_TIMESTAMP = ocel_constants.PARAM_EVENT_TIMESTAMP


def flatten(ocel: OCEL, ot: str, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Flattens the object-centric event log to a traditional event log with the choice of an object type.
    In the flattened log, the objects of a given object type are the cases, and each case
    contains the set of events related to the object.

    Parameters
    -------------------
    ocel
        Object-centric event log
    ot
        Object type
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ACTIVITY
        - Parameters.EVENT_TIMESTAMP

    Returns
    ------------------
    dataframe
        Flattened log in the form of a Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters,
                                                ocel.event_activity)
    event_timestamp = exec_utils.get_param_value(Parameters.EVENT_TIMESTAMP, parameters,
                                                 ocel.event_timestamp)

    objects = ocel.objects[ocel.objects[ocel.object_type_column] == ot]
    objects = objects.rename(columns={ocel.object_id_column: xes_constants.DEFAULT_TRACEID_KEY})
    objects = objects.rename(columns={x: constants.CASE_ATTRIBUTE_PREFIX + x for x in objects.columns})

    relations = ocel.relations[ocel.relations[ocel.object_type_column] == ot][
        [ocel.object_id_column, ocel.event_id_column]]
    relations = relations.rename(columns={ocel.object_id_column: constants.CASE_CONCEPT_NAME})

    objects = objects.merge(relations, on=constants.CASE_CONCEPT_NAME)

    events = ocel.events.merge(objects, on=ocel.event_id_column).rename(
        columns={event_activity: xes_constants.DEFAULT_NAME_KEY, event_timestamp: xes_constants.DEFAULT_TIMESTAMP_KEY})

    return events
