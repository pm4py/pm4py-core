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
from typing import Optional, Dict, Any, List

from pm4py.objects.ocel import constants
from pm4py.objects.ocel.obj import OCEL


def get_attribute_names(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> List[str]:
    """
    Gets the list of attributes at the event and the object level of an object-centric event log
    (e.g. ["cost", "amount", "name"])

    Parameters
    -------------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm

    Returns
    -------------------
    attributes_list
        List of attributes at the event and object level (e.g. ["cost", "amount", "name"])
    """
    if parameters is None:
        parameters = {}

    attributes = sorted(set(x for x in ocel.events.columns if not x.startswith(constants.OCEL_PREFIX)).union(
        x for x in ocel.objects.columns if not x.startswith(constants.OCEL_PREFIX)))

    return attributes
