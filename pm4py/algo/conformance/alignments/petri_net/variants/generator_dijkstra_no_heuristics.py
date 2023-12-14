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

import heapq
import time
from collections.abc import Iterator

from pm4py.objects.log import obj as log_implementation
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.objects.petri_net.utils.synchronous_product import construct_cost_aware, construct
from pm4py.objects.petri_net.utils.petri_utils import construct_trace_net_cost_aware, decorate_places_preset_trans, \
    decorate_transitions_prepostset
from pm4py.objects.petri_net.utils import align_utils as utils
from pm4py.util import exec_utils
from copy import copy
from enum import Enum
import sys
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from typing import Optional, Dict, Any, Union, List as TList
from pm4py.objects.log.obj import Trace
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import typing


class Parameters(Enum):
    PARAM_TRACE_COST_FUNCTION = 'trace_cost_function'
    PARAM_MODEL_COST_FUNCTION = 'model_cost_function'
    PARAM_SYNC_COST_FUNCTION = 'sync_cost_function'
    PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE = 'ret_tuple_as_trans_desc'
    PARAM_TRACE_NET_COSTS = "trace_net_costs"
    TRACE_NET_CONSTR_FUNCTION = "trace_net_constr_function"
    TRACE_NET_COST_AWARE_CONSTR_FUNCTION = "trace_net_cost_aware_constr_function"
    PARAM_MAX_ALIGN_TIME_TRACE = "max_align_time_trace"
    PARAM_MAX_ALIGN_TIME = "max_align_time"
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    VARIANTS_IDX = "variants_idx"


def get_best_worst_cost(petri_net, initial_marking, final_marking, parameters=None):
    """
    Gets the best worst cost of an alignment

    Parameters
    -----------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    -----------
    best_worst_cost
        Best worst cost of alignment
    """
    if parameters is None:
        parameters = {}
    trace = log_implementation.Trace()

    best_worst = next(apply(trace, petri_net, initial_marking, final_marking, parameters=parameters))

    if best_worst is not None:
        return best_worst['cost']

    return None


def apply(trace: Trace, petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Iterator[typing.AlignmentResult]:
    """
    Performs the basic alignment search, given a trace and a net.

    Parameters
    ----------
    trace: :class:`list` input trace, assumed to be a list of events (i.e. the code will use the activity key
    to get the attributes)
    petri_net: :class:`pm4py.objects.petri.net.PetriNet` the Petri net to use in the alignment
    initial_marking: :class:`pm4py.objects.petri.net.Marking` initial marking in the Petri net
    final_marking: :class:`pm4py.objects.petri.net.Marking` final marking in the Petri net
    parameters: :class:`dict` (optional) dictionary containing one of the following:
        Parameters.PARAM_TRACE_COST_FUNCTION: :class:`list` (parameter) mapping of each index of the trace to a positive cost value
        Parameters.PARAM_MODEL_COST_FUNCTION: :class:`dict` (parameter) mapping of each transition in the model to corresponding
        model cost
        Parameters.PARAM_SYNC_COST_FUNCTION: :class:`dict` (parameter) mapping of each transition in the model to corresponding
        synchronous costs
        Parameters.ACTIVITY_KEY: :class:`str` (parameter) key to use to identify the activity described by the events

    Returns
    -------
    dictionary: `dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and **traversed_arcs**
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    trace_cost_function = exec_utils.get_param_value(Parameters.PARAM_TRACE_COST_FUNCTION, parameters, None)
    model_cost_function = exec_utils.get_param_value(Parameters.PARAM_MODEL_COST_FUNCTION, parameters, None)
    trace_net_constr_function = exec_utils.get_param_value(Parameters.TRACE_NET_CONSTR_FUNCTION, parameters,
                                                           None)
    trace_net_cost_aware_constr_function = exec_utils.get_param_value(Parameters.TRACE_NET_COST_AWARE_CONSTR_FUNCTION,
                                                                      parameters, construct_trace_net_cost_aware)

    if trace_cost_function is None:
        trace_cost_function = list(
            map(lambda e: utils.STD_MODEL_LOG_MOVE_COST, trace))
        parameters[Parameters.PARAM_TRACE_COST_FUNCTION] = trace_cost_function

    if model_cost_function is None:
        # reset variables value
        model_cost_function = dict()
        sync_cost_function = dict()
        for t in petri_net.transitions:
            if t.label is not None:
                model_cost_function[t] = utils.STD_MODEL_LOG_MOVE_COST
                sync_cost_function[t] = utils.STD_SYNC_COST
            else:
                model_cost_function[t] = utils.STD_TAU_COST
        parameters[Parameters.PARAM_MODEL_COST_FUNCTION] = model_cost_function
        parameters[Parameters.PARAM_SYNC_COST_FUNCTION] = sync_cost_function

    if trace_net_constr_function is not None:
        # keep the possibility to pass TRACE_NET_CONSTR_FUNCTION in this old version
        trace_net, trace_im, trace_fm = trace_net_constr_function(trace, activity_key=activity_key)
    else:
        trace_net, trace_im, trace_fm, parameters[
            Parameters.PARAM_TRACE_NET_COSTS] = trace_net_cost_aware_constr_function(trace,
                                                                                     trace_cost_function,
                                                                                     activity_key=activity_key)

    yield from apply_trace_net(petri_net, initial_marking, final_marking, trace_net, trace_im, trace_fm, parameters)


def apply_trace_net(petri_net, initial_marking, final_marking, trace_net, trace_im, trace_fm, parameters=None):
    """
        Performs the basic alignment search, given a trace net and a net.

        Parameters
        ----------
        trace: :class:`list` input trace, assumed to be a list of events (i.e. the code will use the activity key
        to get the attributes)
        petri_net: :class:`pm4py.objects.petri.net.PetriNet` the Petri net to use in the alignment
        initial_marking: :class:`pm4py.objects.petri.net.Marking` initial marking in the Petri net
        final_marking: :class:`pm4py.objects.petri.net.Marking` final marking in the Petri net
        parameters: :class:`dict` (optional) dictionary containing one of the following:
            Parameters.PARAM_TRACE_COST_FUNCTION: :class:`list` (parameter) mapping of each index of the trace to a positive cost value
            Parameters.PARAM_MODEL_COST_FUNCTION: :class:`dict` (parameter) mapping of each transition in the model to corresponding
            model cost
            Parameters.PARAM_SYNC_COST_FUNCTION: :class:`dict` (parameter) mapping of each transition in the model to corresponding
            synchronous costs
            Parameters.ACTIVITY_KEY: :class:`str` (parameter) key to use to identify the activity described by the events
            Parameters.PARAM_TRACE_NET_COSTS: :class:`dict` (parameter) mapping between transitions and costs

        Returns
        -------
        dictionary: `dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and **traversed_arcs**
        """
    if parameters is None:
        parameters = {}

    ret_tuple_as_trans_desc = exec_utils.get_param_value(Parameters.PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE,
                                                         parameters, False)

    trace_cost_function = exec_utils.get_param_value(Parameters.PARAM_TRACE_COST_FUNCTION, parameters, None)
    model_cost_function = exec_utils.get_param_value(Parameters.PARAM_MODEL_COST_FUNCTION, parameters, None)
    sync_cost_function = exec_utils.get_param_value(Parameters.PARAM_SYNC_COST_FUNCTION, parameters, None)
    trace_net_costs = exec_utils.get_param_value(Parameters.PARAM_TRACE_NET_COSTS, parameters, None)

    if trace_cost_function is None or model_cost_function is None or sync_cost_function is None:
        sync_prod, sync_initial_marking, sync_final_marking = construct(trace_net, trace_im,
                                                                                                  trace_fm, petri_net,
                                                                                                  initial_marking,
                                                                                                  final_marking,
                                                                                                  utils.SKIP)
        cost_function = utils.construct_standard_cost_function(sync_prod, utils.SKIP)
    else:
        revised_sync = dict()
        for t_trace in trace_net.transitions:
            for t_model in petri_net.transitions:
                if t_trace.label == t_model.label:
                    revised_sync[(t_trace, t_model)] = sync_cost_function[t_model]

        sync_prod, sync_initial_marking, sync_final_marking, cost_function = construct_cost_aware(
            trace_net, trace_im, trace_fm, petri_net, initial_marking, final_marking, utils.SKIP,
            trace_net_costs, model_cost_function, revised_sync)

    max_align_time_trace = exec_utils.get_param_value(Parameters.PARAM_MAX_ALIGN_TIME_TRACE, parameters,
                                                      sys.maxsize)

    yield from apply_sync_prod(sync_prod, sync_initial_marking, sync_final_marking, cost_function,
                           utils.SKIP, ret_tuple_as_trans_desc=ret_tuple_as_trans_desc,
                           max_align_time_trace=max_align_time_trace)



def apply_sync_prod(sync_prod, initial_marking, final_marking, cost_function, skip, ret_tuple_as_trans_desc=False,
                    max_align_time_trace=sys.maxsize):
    yield from __search(sync_prod, initial_marking, final_marking, cost_function, skip,
                    ret_tuple_as_trans_desc=ret_tuple_as_trans_desc, max_align_time_trace=max_align_time_trace)


def __search(sync_net, ini, fin, cost_function, skip, ret_tuple_as_trans_desc=False,
             max_align_time_trace=sys.maxsize):
    start_time = time.time()

    # gviz = vizapply( net=sync_net, initial_marking=ini, final_marking=fin, variant=vizvariant.WO_DECORATION )
    # vizview(gviz)

    decorate_transitions_prepostset(sync_net)
    decorate_places_preset_trans(sync_net)

    closed = set()
    hub:dict[Marking,list[utils.DijkstraSearchTuple]] = dict()
    hub_dist:dict[Marking,int] = dict()
        # Given a marking, holds many tuples of (search tuples that reached it, distance) in two arrays

    ini_state = utils.DijkstraSearchTuple(0, ini, None, None, 0)
    open_set = [ini_state]
    hub[ini_state.m] = [ini_state]
    hub_dist[ini_state.m] = 0
    heapq.heapify(open_set)
    visited = 0
    queued = 0
    traversed = 0

    trans_empty_preset = set(t for t in sync_net.transitions if len(t.in_arcs) == 0)

    while not len(open_set) == 0:
        if (time.time() - start_time) > max_align_time_trace:
            return None

        curr = heapq.heappop(open_set)
        current_marking = curr.m

        # We don't use closed, but check visited path for any loops.
        # if check_cycle_in_searchtuple(curr) :
        #     continue

        # Prevent recursion on already-closed markings (once is enough)
        # Required because multiple paths can add a marking before it get visited.
        already_closed = current_marking in closed
        if already_closed:
            continue

        # print("MARKING[v={},q={},t={},h={}]: {}   {}".format(visited, queued, traversed, len(open_set), repr(current_marking), hash(current_marking)))
        # print(repr_searchtuple(curr))

        closed.add(current_marking)
        visited += 1

        # If we try to expand the `fin` node , then we can be sure that no better (more optimal)
        # paths can exist, since the heap would have visited them before (and there is always a cost
        # to reach the final node).
        if current_marking == fin:
            for alignment in reconstruct_alignment_generator(hub, curr, ret_tuple_as_trans_desc=ret_tuple_as_trans_desc) :
                yield {
                    'alignment': alignment,
                    'cost': curr.g,
                    'visited_states': visited,
                    'queued_states': queued,
                    'traversed_arcs': traversed,
                    'lp_solved': False
                }
            return  # No transition may originate from the fin node.

        enabled_trans = copy(trans_empty_preset)
        for p in current_marking:
            for t in p.ass_trans:
                if t.sub_marking <= current_marking:
                    enabled_trans.add(t)

        trans_to_visit_with_cost = [(t, cost_function[t]) for t in enabled_trans if not (
                t is not None and utils.__is_log_move(t, skip) and utils.__is_model_move(t, skip))]

        for t, cost in trans_to_visit_with_cost:
            traversed += 1
            new_marking = utils.add_markings(current_marking, t.add_marking)  # Counter operations.
            tp = utils.DijkstraSearchTuple(g= curr.g + cost, m= new_marking, p= curr, t= t, l= curr.l + 1)

            # We don't use closed, but check visited path for any loops.
            # if check_cycle_in_searchtuple(tp) :
            #     continue
            if new_marking in closed:
                continue

            # Each marking contains all paths that reached it. Used later for reconstruction.
            # We also make sure that each hub node only contains paths with the minimal distance.
            this_cost = curr.g + cost
            if new_marking not in hub :
                hub[new_marking] = []
                hub_dist[new_marking] = this_cost
            min_cost = hub_dist[new_marking]
            if this_cost < min_cost :
                hub[new_marking] = [tp]
                hub_dist[new_marking] = this_cost
            elif this_cost == min_cost :
                hub[new_marking] = hub[new_marking] + [tp]
            else :
                pass # ignore if this one is bigger

            queued += 1

            heapq.heappush(open_set, tp)



def check_cycle_in_searchtuple ( st: utils.DijkstraSearchTuple ) -> bool :
    rep = set()
    while st is not None :
        if st.m in rep :
            return True
        rep.add(st.m)
        st = st.p
    return False


def repr_searchtuple ( st: utils.DijkstraSearchTuple ) -> str :
    out = []
    while st is not None :
        out.append("{}+{}".format(repr(st.m),hash(st.m)))
        st = st.p
    return " -> ".join(reversed(out))



def rec_hub (hub, curr_m) -> TList[TList[utils.DijkstraSearchTuple]]:

    out = []
    for curr_st in hub[curr_m] :
        if curr_st.p is not None :
            prefixes = rec_hub(hub, curr_st.p.m)
            for pref in prefixes :
                out.append( pref + [curr_st] )
        else :
            out.append( [curr_st] )

    return out


def reconstruct_alignment_generator (
    hub, state:utils.DijkstraSearchTuple, ret_tuple_as_trans_desc=False
):
    # print("Reconstruction at: {}".format(state.m))
    paths = rec_hub(hub, state.m)
    # for hk,hv in sorted(hub.items()) :
    #     print("{:>65} : {}  x  {}".format(
    #         str(hk),
    #         len(hv) if hv is not None else 0,
    #         " , ".join([ ( str(hhv.p.m) if hhv.p is not None else "None" ) for hhv in hv ]),
    #     ))
    for path in paths :
        # print("New alignment:")
        alignment = list()
        for pst in path :
            # print("   {}  -  {}".format(pst.m,pst.t.label if pst.t is not None else "NO-T"))
            if pst.t is not None :
                if ret_tuple_as_trans_desc:
                    alignment.append( (pst.t.name, pst.t.label) )
                else:
                    alignment.append( pst.t.label )

        yield alignment
