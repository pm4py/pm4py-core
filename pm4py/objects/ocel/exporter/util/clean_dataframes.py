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
from typing import Optional, Dict, Any, Tuple

import pandas as pd

from pm4py.objects.ocel.obj import OCEL


def get_dataframes_from_ocel(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[
    pd.DataFrame, pd.DataFrame]:
    if parameters is None:
        parameters = {}

    events = ocel.events.copy()
    for col in events.columns:
        if str(events[col].dtype) == "object":
            events[col] = events[col].astype('string')
        elif "date" in str(events[col].dtype):
            events[col] = events[col].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    objects = ocel.objects.copy()
    for col in objects.columns:
        if str(objects[col].dtype) == "object":
            objects[col] = objects[col].astype('string')
        elif "date" in str(objects[col].dtype):
            objects[col] = objects[col].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    return events, objects
