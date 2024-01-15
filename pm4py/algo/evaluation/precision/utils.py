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
from collections import Counter
from pm4py.objects.log.obj import EventLog, Event, Trace
from pm4py.util import xes_constants as xes_util
import heapq
from pm4py.objects.petri_net.utils.petri_utils import decorate_places_preset_trans, decorate_transitions_prepostset
from pm4py.objects.petri_net.utils import align_utils as utils
from pm4py.objects.petri_net.utils.incidence_matrix import construct
from pm4py.util import constants, pandas_utils
import pandas as pd


def __search(sync_net, ini, fin, stop, cost_function, skip):
    decorate_transitions_prepostset(sync_net)
    decorate_places_preset_trans(sync_net)

    incidence_matrix = construct(sync_net)
    ini_vec, fin_vec, cost_vec = utils.__vectorize_initial_final_cost(incidence_matrix, ini, fin, cost_function)

    closed = set()

    ini_state = utils.SearchTuple(0, 0, 0, ini, None, None, None, True)
    open_set = [ini_state]
    heapq.heapify(open_set)
    visited = 0
    queued = 0
    traversed = 0

    # return all the prefix markings of the optimal alignments as set
    ret_markings = None
    # keep track of the optimal cost of an alignment (to trim search when needed)
    optimal_cost = None

    while not len(open_set) == 0:
        curr = heapq.heappop(open_set)

        current_marking = curr.m

        # trim alignments when we already reached an optimal alignment and the
        # current cost is greater than the optimal cost
        if optimal_cost is not None and curr.f > optimal_cost:
            break

        already_closed = current_marking in closed
        if already_closed:
            continue

        if stop <= current_marking:
            # add the current marking to the set
            # of returned markings
            if ret_markings is None:
                ret_markings = set()
            ret_markings.add(current_marking)
            # close the marking
            closed.add(current_marking)
            # set the optimal cost
            optimal_cost = curr.f

            continue

        closed.add(current_marking)
        visited += 1

        enabled_trans = set()
        for p in current_marking:
            for t in p.ass_trans:
                if t.sub_marking <= current_marking:
                    enabled_trans.add(t)

        trans_to_visit_with_cost = [(t, cost_function[t]) for t in enabled_trans if
                                    not (t is None or utils.__is_log_move(t, skip) or (
                                            utils.__is_model_move(t, skip) and not t.label[1] is None))]

        for t, cost in trans_to_visit_with_cost:
            traversed += 1
            new_marking = utils.add_markings(current_marking, t.add_marking)

            if new_marking in closed:
                continue
            g = curr.g + cost

            queued += 1
            new_f = g

            tp = utils.SearchTuple(new_f, g, 0, new_marking, curr, t, None, True)
            heapq.heappush(open_set, tp)

    return ret_markings


def get_log_prefixes(log, activity_key=xes_util.DEFAULT_NAME_KEY, case_id_key=constants.CASE_CONCEPT_NAME):
    """
    Get log prefixes

    Parameters
    ----------
    log
        Trace log
    activity_key
        Activity key (must be provided if different from concept:name)
    """
    prefixes = {}
    prefix_count = Counter()

    if pandas_utils.check_is_pandas_dataframe(log):
        traces = [tuple(x) for x in log.groupby(case_id_key)[activity_key].agg(list).to_dict().values()]
    else:
        traces = [tuple(x[activity_key] for x in trace) for trace in log]

    for trace in traces:
        for i in range(1, len(trace)):
            prefix = constants.DEFAULT_VARIANT_SEP.join(trace[0:i])
            next_activity = trace[i]
            if prefix not in prefixes:
                prefixes[prefix] = set()
            prefixes[prefix].add(next_activity)
            prefix_count[prefix] += 1

    return prefixes, prefix_count


def form_fake_log(prefixes_keys, activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    Form fake log for replay (putting each prefix as separate trace to align)

    Parameters
    ----------
    prefixes_keys
        Keys of the prefixes (to form a log with a given order)
    activity_key
        Activity key (must be provided if different from concept:name)
    """
    fake_log = EventLog()
    for prefix in prefixes_keys:
        trace = Trace()
        prefix_activities = prefix.split(constants.DEFAULT_VARIANT_SEP)
        for activity in prefix_activities:
            event = Event()
            event[activity_key] = activity
            trace.append(event)
        fake_log.append(trace)
    return fake_log
