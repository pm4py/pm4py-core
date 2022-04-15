__doc__ = """
"""

from typing import List, Optional, Tuple, Dict, Union

from pm4py.objects.log.obj import Trace, EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.utils import get_properties
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns

import pandas as pd
import deprecation


@deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed in a future release.")
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

    me = marking_equation.build(
        petri_net, initial_marking, final_marking, parameters={'costs': cost_function})
    return marking_equation.get_h_value(me)


@deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed in a future release.")
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
    me = extended_marking_equation.build(
        trace, sync_net, sync_im, sync_fm, parameters=parameters)
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


def insert_artificial_start_end(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Union[EventLog, pd.DataFrame]:
    """
    Inserts the artificial start/end activities in an event log / Pandas dataframe

    Parameters
    ------------------
    log
        Event log / Pandas dataframe
    activity_key
        attribute to be used for the activity
    timestamp_key
        attribute to be used for the timestamp
    case_id_key
        attribute to be used as case identifier

    Returns
    ------------------
    log
        Event log / Pandas dataframe with artificial start / end activities
    """
    properties = get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)
        from pm4py.objects.log.util import dataframe_utils
        return dataframe_utils.insert_artificial_start_end(log, parameters=properties)
    else:
        from pm4py.objects.log.util import artificial
        return artificial.insert_artificial_start_end(log, parameters=properties)


def check_is_workflow_net(net: PetriNet) -> bool:
    """
    Checks if the input Petri net satisfies the WF-net conditions:
    1. unique source place
    2. unique sink place
    3. every node is on a path from the source to the sink

    Parameters
    ------------------
    net
        PetriNet

    Returns
    ------------------
    True iff the input net is a WF-net.
    """
    from pm4py.algo.analysis.workflow_net import algorithm
    return algorithm.apply(net)


def maximal_decomposition(net: PetriNet, im: Marking, fm: Marking) -> List[Tuple[PetriNet, Marking, Marking]]:
    """
    Calculate the maximal decomposition of an accepting Petri net.

    Parameters
    ----------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking

    Returns
    ----------------
    list_accepting_nets
        List of accepting Petri nets (Petri net + initial marking + final marking),
        which are the maximal decomposition of the provided accepting Petri net.
    """
    from pm4py.objects.petri_net.utils.decomposition import decompose
    return decompose(net, im, fm)


def generate_marking(net: PetriNet, place_or_dct_places: Union[str, PetriNet.Place, Dict[str, int], Dict[PetriNet.Place, int]]) -> Marking:
    """
    Generate a marking for a given Petri net

    Parameters
    ---------------
    net
        Petri net
    place_or_dct_places
        Place, or dictionary of places, to be used in the marking. Possible values:
        - single Place object for the marking
        - name of the place for the marking
        - dictionary associating to each place its number of tokens
        - dictionary associating to names of places a number of tokens

    Returns
    ----------------
    marking
        Marking object
    """
    dct_places = {x.name: x for x in net.places}
    if isinstance(place_or_dct_places, PetriNet.Place):
        # we specified a single Place object for the marking
        return Marking({place_or_dct_places: 1})
    elif isinstance(place_or_dct_places, str):
        # we specified the name of a place for the marking
        return Marking({dct_places[place_or_dct_places]: 1})
    elif isinstance(place_or_dct_places, dict):
        dct_keys = list(place_or_dct_places)
        if dct_keys:
            if isinstance(dct_keys[0], PetriNet.Place):
                # we specified a dictionary associating to each place its number of tokens
                return Marking(place_or_dct_places)
            elif isinstance(dct_keys[0], str):
                # we specified a dictionary associating to names of places a number of tokens
                return Marking({dct_places[x]: y for x, y in place_or_dct_places.items()})
