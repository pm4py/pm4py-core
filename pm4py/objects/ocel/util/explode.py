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
from copy import deepcopy


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Explode an OCEL: an event associated to N objects is "split" to N events, each one associated to one object.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Possible parameters of the algorithm

    Returns
    -----------------
    ocel
        Exploded object-centric event log
    """
    if parameters is None:
        parameters = {}

    ocel = deepcopy(ocel)
    ocel.relations[ocel.event_id_column] = ocel.relations[ocel.event_id_column] + "_" + ocel.relations[ocel.object_id_column]
    ocel.events = ocel.relations.copy()
    del ocel.events[ocel.object_id_column]
    del ocel.events[ocel.object_type_column]

    return ocel
