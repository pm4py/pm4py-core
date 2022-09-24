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

    :param trace: trace of an event log
    :param petri_net: petri net
    :param initial_marking: initial marking
    :param final_marking: final marking

    :rtype: ``Tuple[PetriNet, Marking, Marking]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        log = pm4py.read_xes('log.xes')
        sync_net, sync_im, sync_fm = pm4py.construct_synchronous_product_net(log[0], net, im, fm)
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

    :param petri_net: petri net
    :param initial_marking: initial marking
    :param final_marking: final marking
    :param cost_function: optional cost function to use when solving the marking equation
    :rtype: ``float``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        heuristic = pm4py.solve_marking_equation(net, im, fm)
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

    :param trace: trace
    :param sync_net: synchronous product net
    :param sync_im: initial marking (of the sync net)
    :param sync_fm: final marking (of the sync net)
    :param split_points: if specified, the indexes of the events of the trace to be used as split points. If not specified, the split points are identified automatically.
    :rtype: ``float``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        log = pm4py.read_xes('log.xes')
        ext_mark_eq_heu = pm4py.solve_extended_marking_equation(log[0], net, im, fm)
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

    :param petri_net: petri net
    :param initial_marking: initial marking
    :param final_marking: final marking
    :rtype: ``bool``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        is_sound = pm4py.check_soundness(net, im, fm)
    """
    from pm4py.algo.analysis.woflan import algorithm as woflan
    return woflan.apply(petri_net, initial_marking, final_marking)


def insert_artificial_start_end(log: Union[EventLog, pd.DataFrame], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> Union[EventLog, pd.DataFrame]:
    """
    Inserts the artificial start/end activities in an event log / Pandas dataframe

    :param log: event log / Pandas dataframe
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Union[EventLog, pd.DataFrame]``

    .. code-block:: python3

        import pm4py

        dataframe = pm4py.insert_artificial_start_end(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
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

    :param net: petri net
    :rtype: ``bool``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        is_wfnet = pm4py.check_is_workflow_net(net, im, fm)
    """
    from pm4py.algo.analysis.workflow_net import algorithm
    return algorithm.apply(net)


def maximal_decomposition(net: PetriNet, im: Marking, fm: Marking) -> List[Tuple[PetriNet, Marking, Marking]]:
    """
    Calculate the maximal decomposition of an accepting Petri net.

    :param net: petri net
    :param im: initial marking
    :param fm: final marking
    :rtype: ``List[Tuple[PetriNet, Marking, Marking]]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        list_nets = pm4py.maximal_decomposition(net, im, fm)
        for anet in list_nets:
            subnet, subim, subfm = anet
            pm4py.view_petri_net(subnet, subim, subfm, format='svg')
    """
    from pm4py.objects.petri_net.utils.decomposition import decompose
    return decompose(net, im, fm)


def generate_marking(net: PetriNet, place_or_dct_places: Union[str, PetriNet.Place, Dict[str, int], Dict[PetriNet.Place, int]]) -> Marking:
    """
    Generate a marking for a given Petri net

    :param net: petri net
    :param place_or_dct_places: place, or dictionary of places, to be used in the marking. Possible values: single Place object for the marking; name of the place for the marking; dictionary associating to each place its number of tokens; dictionary associating to names of places a number of tokens.
    :rtype: ``Marking``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.read_pnml('model.pnml')
        marking = pm4py.generate_marking(net, {'source': 2})
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
