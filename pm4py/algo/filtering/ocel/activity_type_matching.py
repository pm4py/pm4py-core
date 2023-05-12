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
from copy import deepcopy
from typing import Dict, Any, Optional, Collection
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel import constants as ocel_constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE
    TEMP_COLUMN = "temp_column"
    TEMP_SEPARATOR = "temp_separator"


def apply(ocel: OCEL, correspondence_dict: Dict[str, Collection[str]],
          parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Filters an object-centric event log keeping only the specified object types
    with the specified activity set (filters out the rest).

    Parameters
    ----------------
    ocel
        Object-centric event log
    correspondence_dict
        Dictionary containing, for every object type of interest, a
        collection of allowed activities.  Example:

        {"order": ["Create Order"], "element": ["Create Order", "Create Delivery"]}

        Keeps only the object types "order" and "element".
        For the "order" object type, only the activity "Create Order" is kept.
        For the "element" object type, only the activities "Create Order" and "Create Delivery" are kept.
    parameters
        Parameters of the algorithm, including:
            - Parameters.ACTIVITY_KEY => the activity key
            - Parameters.OBJECT_TYPE => the object type column

    Returns
    -----------------
    filtered_ocel
        Filtered object-centric event log
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, ocel.event_activity)
    object_type_column = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)
    temp_column = exec_utils.get_param_value(Parameters.TEMP_COLUMN, parameters, "@@temp_column")
    temp_separator = exec_utils.get_param_value(Parameters.TEMP_SEPARATOR, parameters, "@#@#")

    ocel = deepcopy(ocel)

    inv_dict = set()
    for ot in correspondence_dict:
        for act in correspondence_dict[ot]:
            inv_dict.add(act + temp_separator + ot)

    ocel.relations[temp_column] = ocel.relations[activity_key] + temp_separator + ocel.relations[object_type_column]
    ocel.relations = ocel.relations[ocel.relations[temp_column].isin(inv_dict)]

    del ocel.relations[temp_column]

    return filtering_utils.propagate_relations_filtering(ocel, parameters=parameters)
