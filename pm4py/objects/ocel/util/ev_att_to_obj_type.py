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
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.objects.ocel import constants
from pm4py.util import exec_utils
from copy import deepcopy
import pandas as pd


class Parameters(Enum):
    EVENT_ID = constants.PARAM_EVENT_ID
    EVENT_ACTIVITY = constants.PARAM_EVENT_ACTIVITY
    EVENT_TIMESTAMP = constants.PARAM_EVENT_TIMESTAMP
    OBJECT_ID = constants.PARAM_OBJECT_ID
    OBJECT_TYPE = constants.PARAM_OBJECT_TYPE
    INTERNAL_INDEX = constants.PARAM_INTERNAL_INDEX


def apply(ocel: OCEL, param: str, parameters: Optional[Dict[Any, Any]] = None):
    """
    Transforms an event attribute to an object type.

    Parameters
    ---------------
    ocel
        Object-centric event log
    param
        Event attribute that should be moved at the event level
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID => the event identifier column
        - Parameters.EVENT_ACTIVITY => the event activity column
        - Parameters.EVENT_TIMESTAMP => the event timestamp column
        - Parameters.OBJECT_ID => the object identifier column
        - Parameters.OBJECT_TYPE => the object type column
        - Parameters.INTERNAL_INDEX => the internal index

    Returns
    --------------
    new_ocel
        OCEL in which the attribute has been moved to the object type level.
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters, ocel.event_activity)
    event_timestamp = exec_utils.get_param_value(Parameters.EVENT_TIMESTAMP, parameters, ocel.event_timestamp)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel.object_id_column)
    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)
    internal_index = exec_utils.get_param_value(Parameters.INTERNAL_INDEX, parameters, constants.DEFAULT_INTERNAL_INDEX)

    new_ocel = deepcopy(ocel)
    new_ocel.events[param] = new_ocel.events[param].astype(str)
    ev_param = new_ocel.events.dropna(subset=[param])[[event_id, event_activity, event_timestamp, param]]
    vals = set(ev_param[param].unique())
    ev_param = ev_param.rename(columns={param: object_id})
    ev_param[object_type] = param

    new_objects_df = pd.DataFrame([{object_id: v, object_type: param} for v in vals])

    new_ocel.objects = pd.concat([new_ocel.objects, new_objects_df])
    new_ocel.relations = pd.concat([new_ocel.relations, ev_param])

    new_ocel.relations[internal_index] = new_ocel.relations.index

    new_ocel.relations = new_ocel.relations.sort_values([event_timestamp, internal_index])

    del new_ocel.events[param]

    return new_ocel
