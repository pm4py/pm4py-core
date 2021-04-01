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
from pm4py.objects.log import obj
import logging

def empty_trace_filtering(l, f):
    enough_traces = False
    empty_traces_present, counter = __count_empty_traces(l)
    if counter >= len(l)*f:
        enough_traces = True

    if empty_traces_present:
        new_log = obj.EventLog()
        for trace in l:
            if len(trace) != 0:
                new_log.append(trace)
        return empty_traces_present, enough_traces, new_log
    else:
        return False, False, l


def __count_empty_traces(l):
    counter = 0
    empty_traces_present = False
    for trace in l:
        if len(trace) == 0:
            empty_traces_present = True
            counter += 1

    return empty_traces_present, counter
