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
from typing import List

import pandas as pd

from pm4py.objects.ocel.obj import OCEL


def ocel_get_object_types(ocel: OCEL) -> List[str]:
    """
    Gets the list of object types contained in the object-centric event log
    (e.g., ["order", "item", "delivery"]).

    Parameters
    -----------------
    ocel
        Object-centric event log

    Returns
    ----------------
    object_types_list
        List of object types contained in the event log (e.g., ["order", "item", "delivery"])
    """
    return list(ocel.objects[ocel.object_type_column].unique())


def ocel_get_attribute_names(ocel: OCEL) -> List[str]:
    """
    Gets the list of attributes at the event and the object level of an object-centric event log
    (e.g. ["cost", "amount", "name"])

    Parameters
    -------------------
    ocel
        Object-centric event log

    Returns
    -------------------
    attributes_list
        List of attributes at the event and object level (e.g. ["cost", "amount", "name"])
    """
    from pm4py.objects.ocel.util import attributes_names
    return attributes_names.get_attribute_names(ocel)


def ocel_flattening(ocel: OCEL, object_type: str) -> pd.DataFrame:
    """
    Flattens the object-centric event log to a traditional event log with the choice of an object type.
    In the flattened log, the objects of a given object type are the cases, and each case
    contains the set of events related to the object.

    Parameters
    -------------------
    ocel
        Object-centric event log
    object_type
        Object type

    Returns
    ------------------
    dataframe
        Flattened log in the form of a Pandas dataframe
    """
    from pm4py.objects.ocel.util import flattening
    return flattening.flatten(ocel, object_type)
