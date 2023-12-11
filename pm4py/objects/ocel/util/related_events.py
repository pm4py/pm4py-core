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
from typing import Dict, Any, Optional, List

from pm4py.objects.ocel.obj import OCEL
from pm4py.util import pandas_utils


def related_events_dct(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Dict[str, List[str]]]:
    if parameters is None:
        parameters = {}

    object_types = pandas_utils.format_unique(ocel.relations[ocel.object_type_column].unique())
    dct = {}
    for ot in object_types:
        dct[ot] = ocel.relations[ocel.relations[ocel.object_type_column] == ot].groupby(ocel.object_id_column)[ocel.event_id_column].apply(
            list).to_dict()
    return dct
