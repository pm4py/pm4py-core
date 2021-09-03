from typing import List, Optional, Tuple, Dict

from pm4py.objects.log.obj import Trace, EventLog, Event
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import constants, xes_constants
from pm4py.utils import get_properties
from copy import deepcopy


def insert_artificial_start_end_activities(log: EventLog):
    """
    Inserts artificial start (▶) and end (■) activities at beginning and end of each case of the log

    Parameters
    ------------------
    log
        Event log

    Returns
    -----------------
    log_with_artificial_sa_and_ea
        Log with artificial start and end activities
    """
    log = deepcopy(log)
    properties = get_properties(log)
    activity_key = properties[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in properties else xes_constants.DEFAULT_NAME_KEY
    for trace in log:
        trace.insert(0, Event({activity_key: "▶"}))
        trace.append(Event({activity_key: "■"}))
    return log


def construct_synchronous_product_net(trace: Trace, petri_net: PetriNet, initial_marking: Marking,
                                      final_marking: Marking) -> Tuple[PetriNet, Marking, Marking]:
    """
    constructs the synchronous product net between a trace and a Petri net process model.

    Parameters
    ----------------
    trace
        Trace of an event log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    ----------------
    sync_net
        Synchronous product net
    sync_im
        Initial marking of the sync net
    sync_fm
        Final marking of the sync net
    """
    from pm4py.objects.petri_net.utils.petri_utils import construct_trace_net
    from pm4py.objects.petri_net.utils.synchronous_product import construct
    from pm4py.objects.petri_net.utils.align_utils import SKIP
    trace_net, trace_im, trace_fm = construct_trace_net(trace)
    sync_net, sync_im, sync_fm = construct(trace_net, trace_im, trace_fm, petri_net, initial_marking, final_marking,
                                           SKIP)
    return sync_net, sync_im, sync_fm


def solve_marking_equation(petri_net: PetriNet, initial_marking: Marking,
                           final_marking: Marking, cost_function: Dict[PetriNet.Transition, float] = None) -> float:
    """
    Solves the marking equation of a Petri net.
    The marking equation is solved as an ILP problem.
    An optional transition-based cost function to minimize can be provided as well.

    Parameters
    ---------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    cost_function
        optional cost function to use when solving the marking equation.

    Returns
    ----------------
    h_value
        Heuristics value calculated resolving the marking equation
    """
    from pm4py.algo.analysis.marking_equation import algorithm as marking_equation

    if cost_function is None:
        cost_function = dict()
        for t in petri_net.transitions:
            cost_function[t] = 1

    me = marking_equation.build(petri_net, initial_marking, final_marking, parameters={'costs': cost_function})
    return marking_equation.get_h_value(me)


def solve_extended_marking_equation(trace: Trace, sync_net: PetriNet, sync_im: Marking,
                                    sync_fm: Marking, split_points: Optional[List[int]] = None) -> float:
    """
    Gets an heuristics value (underestimation of the cost of an alignment) between a trace
    and a synchronous product net using the extended marking equation with the standard cost function
    (e.g. sync moves get cost equal to 0, invisible moves get cost equal to 1,
    other move on model / move on log get cost equal to 10000), with an optimal provisioning of the split
    points

    Parameters
    ----------------
    trace
        Trace
    sync_net
        Synchronous product net
    sync_im
        Initial marking (of the sync net)
    sync_fm
        Final marking (of the sync net)
    split_points
        If specified, the indexes of the events of the trace to be used as split points.
        If not specified, the split points are identified automatically

    Returns
    ----------------
    h_value
        Heuristics value calculated resolving the marking equation
    """
    from pm4py.algo.analysis.extended_marking_equation import algorithm as extended_marking_equation
    parameters = {}
    if split_points is not None:
        parameters[extended_marking_equation.Variants.CLASSIC.value.Parameters.SPLIT_IDX] = split_points
    me = extended_marking_equation.build(trace, sync_net, sync_im, sync_fm, parameters=parameters)
    return extended_marking_equation.get_h_value(me)


def check_soundness(petri_net: PetriNet, initial_marking: Marking,
                    final_marking: Marking) -> bool:
    """
    Check if a given Petri net is a sound WF-net.
    A Petri net is a WF-net iff:
        - it has a unique source place
        - it has a unique end place
        - every element in the WF-net is on a path from the source to the sink place
    A WF-net is sound iff:
        - it contains no live-locks
        - it contains no deadlocks
        - we are able to always reach the final marking
    For a formal definition of sound WF-net, consider: http://www.padsweb.rwth-aachen.de/wvdaalst/publications/p628.pdf


    Parameters
    ---------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    --------------
    boolean
        Soundness
    """
    from pm4py.algo.analysis.woflan import algorithm as woflan
    return woflan.apply(petri_net, initial_marking, final_marking)
