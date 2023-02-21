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
from pm4py.util import constants
from pm4py.objects.ocel import constants as ocel_constants
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any, Collection


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE
    TEMP_COLUMN = "temp_column"
    TEMP_SEPARATOR = "temp_separator"


def get_object_type_activities(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Collection[str]]:
    """
    Gets the set of activities performed for each object type

    Parameters
    ----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the activity key
        - Parameters.OBJECT_TYPE => the object type column

    Returns
    ----------------
    dict
        A dictionary having as key the object types and as values the activities performed for that object type
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, ocel.event_activity)
    object_type_column = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)

    matching_dict = {}
    prel_dict = ocel.relations.groupby([activity_key, object_type_column]).size().to_dict()

    for el in prel_dict:
        if not el[1] in matching_dict:
            matching_dict[el[1]] = set()
        matching_dict[el[1]].add(el[0])

    return matching_dict
