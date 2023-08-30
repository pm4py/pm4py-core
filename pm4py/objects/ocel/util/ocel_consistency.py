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


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Forces the consistency of the OCEL, ensuring that the event/object identifier,
    event/object type are of type string and non-empty.

    Parameters
    --------------
    ocel
        OCEL
    parameters
        Possible parameters of the method

    Returns
    --------------
    ocel
        Consistent OCEL
    """
    if parameters is None:
        parameters = {}

    fields = {
        "events": ["ocel:eid", "ocel:activity"],
        "objects": ["ocel:oid", "ocel:type"],
        "relations": ["ocel:eid", "ocel:oid", "ocel:activity", "ocel:type"],
        "o2o": ["ocel:oid", "ocel:oid_2"],
        "e2e": ["ocel:eid", "ocel:eid_2"],
        "object_changes": ["ocel:oid"]
    }

    for tab in fields:
        df = getattr(ocel, tab)
        for fie in fields[tab]:
            df = df.dropna(subset=[fie], how="any")
            df[fie] = df[fie].astype("string")
            df = df.dropna(subset=[fie], how="any")
            df = df[df[fie].str.len() > 0]
            setattr(ocel, tab, df)

    return ocel
