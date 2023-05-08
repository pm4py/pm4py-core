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
from pm4py.algo.discovery.ocel.ocdfg import algorithm as ocdfg_disc
import numpy as np
from enum import Enum
from pm4py.util import exec_utils, constants


class Parameters(Enum):
    MAX_LEN = "max_len"
    INCLUDE_HEADER = "include_header"
    INCLUDE_PERFORMANCE = "include_performance"


def __get_descr(curr, include_performance):
    stru = "  \"%s\" -> \"%s\" (frequency (number of events) = %d, frequency (number of objects) = %d" % (
    curr[1][0], curr[1][1], curr[2], curr[3])
    if include_performance:
        stru += ", duration = %.2f" % curr[5]
    stru += ")\n"
    return stru


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    max_len = exec_utils.get_param_value(Parameters.MAX_LEN, parameters, constants.OPENAI_MAX_LEN)
    include_header = exec_utils.get_param_value(Parameters.INCLUDE_HEADER, parameters, True)
    include_performance = exec_utils.get_param_value(Parameters.INCLUDE_PERFORMANCE, parameters, True)

    ocdfg = ocdfg_disc.apply(ocel, parameters=parameters)

    object_types = sorted(list(ocdfg["edges"]["total_objects"].keys()))
    edges = set()
    for ot in object_types:
        for e in ocdfg["edges"]["event_couples"][ot]:
            edges.add((ot, e))

    edges_values = []
    for obj in edges:
        ot = obj[0]
        e = obj[1]
        edges_values.append([obj[0], obj[1],
                             len(ocdfg["edges"]["event_couples"][ot][e]),
                             len(ocdfg["edges"]["unique_objects"][ot][e]),
                             len(ocdfg["edges"]["total_objects"][ot][e]),
                             float(np.average(ocdfg["edges_performance"]["event_couples"][ot][e])),
                             float(np.average(ocdfg["edges_performance"]["total_objects"][ot][e]))
        ])

    edges_values = sorted(edges_values, key=lambda x: (x[2], x[5], x[0], x[1]), reverse=True)

    i = 0
    curr_len = 0
    while i < len(edges_values):
        if curr_len >= max_len:
            break

        stru = __get_descr(edges_values[i], include_performance)
        curr_len += len(stru)

        i = i + 1

    edges_values = edges_values[:i]
    ot_edges = {}

    for edg in edges_values:
        if not edg[0] in ot_edges:
            ot_edges[edg[0]] = []

        ot_edges[edg[0]].append(edg)

    ret = ["\n"]
    if include_header:
        ret.append("If I have an object-centric event log with the following directly follows graph (split between the different object types):\n")

        for ot in ot_edges:
            ret.append("\nObject type: %s\n" % (ot))
            for edg in ot_edges[ot]:
                ret.append(__get_descr(edg, include_performance))

    ret.append("\n")

    return "".join(ret)
