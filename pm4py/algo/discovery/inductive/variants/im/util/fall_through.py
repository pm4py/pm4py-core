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
from copy import copy, deepcopy
import logging


def show_nice_log(old_log):
    nl = []
    for trace in old_log:
        nt = []
        for element in trace:
            nt.append(element['concept:name'])
        nl.append(nt)
    return nl


def empty_trace(l):
    # checks if there are empty traces in the log, if so, creates new_log without those empty traces
    contains_empty_trace = False
    for trace in l:
        if len(trace) == 0:
            contains_empty_trace = True

    if contains_empty_trace:
        new_log = obj.EventLog()
        for trace in l:
            if len(trace) != 0:
                new_log.append(trace)
        return True, new_log
    else:
        return False, l


def filter_activity_from_log(l, act, activity_key):
    # remove the activity from every trace in the log
    # as trace doesnt have remove function, we just create new traces without chosen_activity
    act_str = str(act)
    new_log = obj.EventLog()
    for trace in l:
        new_trace = obj.Trace()
        for event in trace:
            if not event[activity_key] == act_str:
                new_trace.append(event)
        new_log.append(new_trace)

    return new_log


def index_containing(l, activities, activity_key):
    ret = {act: [] for act in activities}
    for index, trace in enumerate(l):
        activities = set(ev[activity_key] for ev in trace)
        for act in activities:
            ret[act].append(index)

    return ret


def filter_activity_use_idx(l, act, activity_key, idx):
    act_str = str(act)
    i_act = idx[act]
    new_log = obj.EventLog()
    i = 0
    j = 0
    while i < len(l):
        if j < len(i_act) and i == i_act[j]:
            new_trace = obj.Trace()
            for event in l[i]:
                if not event[activity_key] == act_str:
                    new_trace.append(event)
            new_log.append(new_trace)
            j = j + 1
        else:
            new_log.append(l[i])
        i = i + 1
    return new_log


def act_once_per_trace(l, activities, activity_key):
    small_log = obj.EventLog()
    small_trace = obj.Trace()
    new_log = obj.EventLog()
    number_of_traces = len(l)
    possible_activities = list()
    # transform dict of activities to list
    activities_dict = activities
    for key, value in activities_dict.items():
        # if activity appears as often as there are traces, add to list of possible activities:
        if value == number_of_traces:
            possible_activities.append(key)

    chosen_activity = None
    # find an activity that appears exactly once per trace and save it in chose_activity
    for act in possible_activities:
        fits_log = True
        for trace in l:
            fits_trace = False
            for element in trace:
                # enough to check if element occurs once per trace as number of occurrences equals the number of traces
                if act == element[activity_key]:
                    fits_trace = True
            if not fits_trace:
                fits_log = False

        if fits_log:
            chosen_activity = act
            break

    # save the chosen activity in a new trace, so that it can later be appended as leaf to our subtree
    for trace in l:
        if len(small_trace) > 0:
            break
        for element in trace:
            if element[activity_key] == chosen_activity:
                small_trace.append(element)
                small_log.append(small_trace)
                break

    if chosen_activity is not None:
        new_log = filter_activity_from_log(l, chosen_activity, activity_key)
        logging_output = "activity once per trace: " + str(chosen_activity)
        logging.debug(logging_output)
        return True, new_log, small_log
    else:
        return False, new_log, chosen_activity


def activity_concurrent(self, l, activities, activity_key, parameters=None):
    from pm4py.algo.discovery.inductive.variants.im.data_structures import subtree_plain as subtree

    small_log = obj.EventLog()
    test_log = obj.EventLog()
    key = None
    activities_copy = copy(activities)
    empty_trace = obj.Trace()
    idx = index_containing(l, activities, activity_key)

    for key, value in activities_copy.items():  # iterate through activities (saved in key)

        test_log = filter_activity_use_idx(l, key, activity_key, idx)
        #test_log = filter_activity_from_log(l, key, activity_key)
        # unsure about this one:
        contains_empty_trace = False
        for trace in test_log:
            if len(trace) == 0:
                contains_empty_trace = True
        if contains_empty_trace:
            continue

        # more efficient deepcopy
        self_copy = deepcopy(self)
        cut = subtree.SubtreePlain.check_for_cut(self_copy, test_log,
                                                 key, parameters=parameters)  # check if leaving out act, leads to finding cut
        if cut:
            # save act to small_trace, so that it can be appended as leaf later on
            for trace in l:
                small_trace = obj.Trace()
                contains_activity = False
                for element in trace:
                    if element[activity_key] == key:
                        contains_activity = True
                        small_trace.append(element)
                small_log.append(small_trace)

                if not contains_activity:
                    small_log.append(empty_trace)
            logging_output = "activity concurrent: " + str(key)
            logging.debug(logging_output)
            return True, test_log, small_log, key  # if so, return new log

    return False, test_log, small_log, key  # if,  after iterating through all act's still no cut is found, return false


def split_between_end_and_start(trace, start_activities, end_activities, activity_key):
    # splits a trace between the first occurrence of an end activity  following a start activity
    found_split = False
    new_trace_1 = obj.Trace()
    new_trace_2 = obj.Trace()
    i = 0

    while not found_split and i < len(trace) - 1:
        if trace[i][activity_key] in end_activities and trace[i + 1][activity_key] in start_activities:
            found_split = True
            j = 0
            while j <= i:
                new_trace_1.append(trace[j])
                j += 1
            for k in range(i + 1, len(trace)):
                new_trace_2.append(trace[k])
            break
        else:
            i += 1
    if not found_split:
        new_trace_1 = trace
    return new_trace_1, new_trace_2, found_split


def strict_tau_loop(l, start_activities, end_activities, activity_key):
    new_log = obj.EventLog()
    for trace in l:  # for all traces
        t1, t2, found_split = split_between_end_and_start(trace, start_activities, end_activities,
                                                          activity_key)  # look for split
        if found_split:
            new_log.append(t1)
            while found_split:  # if split is found
                t1, t2, found_split = split_between_end_and_start(t2, start_activities,
                                                                  end_activities, activity_key)  # continue to split
                new_log.append(t1)
        else:
            new_log.append(trace)  # if there is nothing to split, append the whole trace

    if len(new_log) > len(l):
        logging.debug("strict_tau_loop")
        return True, new_log
    else:
        return False, new_log


def split_before_start(trace, start_activities, activity_key):
    # if there is only one activity, there is nothing to split
    if len(trace) == 1:
        return trace, trace, False
    # if none of the above cases apply, we split at the occurence of a start activity
    found_split = False
    new_trace_1 = obj.Trace()
    new_trace_2 = obj.Trace()
    i = 1
    while not found_split and i < len(trace):  # for all events in trace
        if trace[i][activity_key] in start_activities and len(trace) > 1:
            found_split = True
            for j in range(0, i):
                new_trace_1.append(trace[j])
            for k in range(i, len(trace)):
                new_trace_2.append(trace[k])
        i += 1

    return new_trace_1, new_trace_2, found_split


def tau_loop(l, start_activities, activity_key):
    # pretty much the same code as in strict_tau_loop, just that we split at a different point
    new_log = obj.EventLog()
    for trace in l:
        t1, t2, found_split = split_before_start(trace, start_activities, activity_key)
        if found_split and len(t2) != 0:
            new_log.append(t1)
            while found_split:
                t2_backup = copy(t2)
                t1, t2, found_split = split_before_start(t2, start_activities, activity_key)
                if len(t1) != 0:
                    new_log.append(t1)
                else:
                    new_log.append(t2_backup)
        else:
            new_log.append(trace)

    if len(new_log) > len(l):
        logging.debug("tau_loop")
        return True, new_log
    else:
        return False, new_log
