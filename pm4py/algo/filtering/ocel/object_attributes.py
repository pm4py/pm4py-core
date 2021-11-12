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
from typing import Dict, Any, Optional, Collection
from pm4py.objects.ocel.obj import OCEL


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    POSITIVE = "positive"


def apply(ocel: OCEL, values: Collection[Any], parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Filters the object-centric event log on the provided object attributes values

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

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, ocel.object_type_column)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    ocel = copy(ocel)
    if positive:
        ocel.objects = ocel.objects[ocel.objects[attribute_key].isin(values)]
    else:
        ocel.objects = ocel.objects[~ocel.objects[attribute_key].isin(values)]

    return filtering_utils.propagate_object_filtering(ocel, parameters=parameters)
