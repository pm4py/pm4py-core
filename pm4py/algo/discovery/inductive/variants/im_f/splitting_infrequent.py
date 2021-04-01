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


def filter_trace_on_cut_partition(trace, partition, activity_key):
    filtered_trace = obj.Trace()
    for event in trace:
        if event[activity_key] in partition:
            filtered_trace.append(event)
    return filtered_trace


def find_split_point(trace, cut_partition, start, ignore, activity_key):
    possibly_best_before_first_activity = False
    least_cost = start
    position_with_least_cost = start
    cost = float(0)
    i = start
    while i < len(trace):
        if trace[i][activity_key] in cut_partition:
            cost = cost-1
        elif trace[i][activity_key] not in ignore:
            # use bool variable for the case, that the best split is before the first activity
            if i == 0:
                possibly_best_before_first_activity = True
            cost = cost+1
        if cost <= least_cost:
            least_cost = cost
            position_with_least_cost = i+1
        i += 1
    if possibly_best_before_first_activity and position_with_least_cost == 1:
        position_with_least_cost = 0
    return position_with_least_cost


def cut_trace_between_two_points(trace, point_a, point_b):
    cutted_trace = obj.Trace()
    # we have to use <= although in the paper the intervall is [) because our index starts at 0
    while point_a < point_b:
        cutted_trace.append(trace[point_a])
        point_a += 1

    return cutted_trace


def split_xor_infrequent(cut, l, activity_key):
    # TODO think of empty logs
    # creating the empty L_1,...,L_n from the second code-line on page 205
    n = len(cut)
    new_logs = [obj.EventLog() for i in range(0, n)]
    for trace in l:                                                 # for all traces
        number_of_events_in_trace = 0
        index_of_cut_partition = 0
        i = 0
        # use i as index here so that we can write in L_i
        for i in range(0, len(cut)):                                # for all cut partitions
            temp_counter = 0
            for event in trace:                                     # for all events in current trace
                if event[activity_key] in cut[i]:                 # count amount of events from trace in partition
                    temp_counter += 1
            if temp_counter > number_of_events_in_trace:
                number_of_events_in_trace = temp_counter
                index_of_cut_partition = i
        filtered_trace = filter_trace_on_cut_partition(trace, cut[index_of_cut_partition], activity_key)
        new_logs[index_of_cut_partition].append(filtered_trace)
    return new_logs


def split_sequence_infrequent(cut, l, activity_key):
    # write L_1,...,L_n like in second line of code on page 206
    n = len(cut)
    new_logs = [obj.EventLog() for j in range(0, n)]
    ignore = []
    split_points_list = [0] * len(l)
    for i in range(0, n):
        split_point = 0
        # write our ignore list with all elements from past cut partitions
        if i != 0:
            for element in cut[i-1]:
                ignore.append(element)
        for j in range(len(l)):
            trace = l[j]
            new_split_point = find_split_point(trace, cut[i], split_points_list[j], ignore, activity_key)
            cutted_trace = cut_trace_between_two_points(trace, split_points_list[j], new_split_point)
            filtered_trace = filter_trace_on_cut_partition(cutted_trace, cut[i], activity_key)
            new_logs[i].append(filtered_trace)
            split_points_list[j] = new_split_point
    return new_logs


def split_loop_infrequent(cut, l, activity_key):
    n = len(cut)
    new_logs = [obj.EventLog() for i in range(0, n)]
    for trace in l:
        s = cut[0]
        st = obj.Trace()
        for act in trace:
            if act in s:
                st.insert(act)
            else:
                j = 0
                for j in range(0, len(cut)):
                    if cut[j] == s:
                        break
                new_logs[j].append(st)
                st = obj.Trace()
                for partition in cut:
                    if act[activity_key] in partition:
                        s.append(partition)
        # L_j <- L_j + [st] with sigma_j = s
        j = 0
        for j in range(0, len(cut)):
            if cut[j] == s:
                break
        new_logs[j].append(st)
        if s != cut[0]:
            new_logs[0].append(obj.EventLog())

    return new_logs
