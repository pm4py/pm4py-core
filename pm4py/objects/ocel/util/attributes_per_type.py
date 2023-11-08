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
from pm4py.objects.ocel import constants
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    EVENT_ACTIVITY = constants.PARAM_EVENT_ACTIVITY
    OBJECT_TYPE = constants.PARAM_OBJECT_TYPE


def get(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    if parameters is None:
        parameters = {}

    event_activity_column = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters, ocel.event_activity)
    object_type_column = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)

    ets = {k: {x: str(v[x].dtype) for x in v.dropna(axis="columns", how="all").columns if not x.startswith("ocel:")} for k, v in ocel.events.groupby(event_activity_column)}
    ots = {k: {x: str(v[x].dtype) for x in v.dropna(axis="columns", how="all").columns if not x.startswith("ocel:")} for k, v in ocel.objects.groupby(object_type_column)}
    ots2 = {k: {x: str(v[x].dtype) for x in v.dropna(axis="columns", how="all").columns if not x.startswith("ocel:")} for k, v in ocel.object_changes.groupby(object_type_column)}

    for k in ots2:
        if k not in ots:
            ots[k] = ots2[k]
        else:
            for x in ots2[k]:
                if x not in ots[k]:
                    ots[k][x] = ots2[k][x]

    return ets, ots
