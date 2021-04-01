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


def split_xor(cut, l, activity_key):
    new_logs = []
    for c in cut:  # for cut partition
        lo = obj.EventLog()
        for i in range(0, len(l)):  # for trace in log
            fits = True
            for j in range(0, len(l[i])):  # for event in trace
                if l[i][j][activity_key] not in c:
                    fits = False  # if not every event fits the current cut-partition, we don't add it's trace
            if fits:
                lo.append(l[i])
        new_logs.append(lo)

    return new_logs  # new_logs is a list that contains logs


def split_parallel(cut, l, activity_key):
    new_logs = []
    for c in cut:
        lo = obj.EventLog()
        for trace in l:
            new_trace = obj.Trace()
            for event in trace:
                if event[activity_key] in c:
                    new_trace.append(event)
            lo.append(new_trace)
        new_logs.append(lo)
    return new_logs


def split_sequence(cut, l, activity_key):
    new_logs = []
    for c in cut:  # for all cut-partitions
        lo = obj.EventLog()
        for trace in l:  # for all traces in the log
            not_in_c = True
            trace_new = obj.Trace()
            for j in range(0, len(trace)):  # for every event in the current trace
                if trace[j][activity_key] in c:
                    not_in_c = False
                    while trace[j][activity_key] in c:
                        trace_new.append(trace[j])  # we only add the events that match the cut partition
                        if j + 1 < len(trace):
                            j += 1
                        else:
                            j += 1
                            break
                    lo.append(trace_new)
                    break
            if not_in_c:
                lo.append(trace_new)
        new_logs.append(lo)
    if len(new_logs) > 0:
        return new_logs


def split_loop(cut, l, activity_key):
    new_logs = []
    for c in cut:  # for cut partition
        lo = obj.EventLog()
        for trace in l:  # for all traces
            j = 0
            while j in range(0, len(trace)):  # for all events
                if trace[j][activity_key] in c:
                    trace_new = obj.Trace()
                    # declared here and not above, so that we can generate multiple traces from one trace and
                    # cut (repetition)
                    # append those events that are contained in c:
                    while trace[j][activity_key] in c:
                        trace_new.append(trace[j])
                        if j + 1 < len(trace):
                            j += 1
                        else:
                            j += 1
                            break
                    lo.append(trace_new)
                else:
                    j += 1

        if len(lo) != 0:
            new_logs.append(lo)

    return new_logs
