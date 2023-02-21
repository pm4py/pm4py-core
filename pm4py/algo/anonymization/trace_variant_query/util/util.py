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

import datetime

from dateutil.tz import tzutc

from pm4py.objects.log import obj

TRACE_START = "TRACE_START"
TRACE_END = "TRACE_END"
EVENT_DELIMETER = ">>>"


def generate_pm4py_log(trace_frequencies):
    log = obj.EventLog()
    trace_count = 0
    for variant in trace_frequencies.items():
        frequency = variant[1]
        activities = variant[0].split(EVENT_DELIMETER)
        for i in range(0, frequency):
            trace = obj.Trace()
            trace.attributes["concept:name"] = trace_count
            trace_count = trace_count + 1
            for activity in activities:
                if not TRACE_END in activity:
                    event = obj.Event()
                    event["concept:name"] = str(activity)
                    event["time:timestamp"] = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=tzutc())
                    trace.append(event)
            log.append(trace)
    return log
