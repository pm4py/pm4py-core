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
from pm4py.objects.petri_net.utils import reachability_graph
import itertools
from enum import Enum
from typing import Optional, Dict, Any
from pm4py.objects.petri_net.obj import PetriNet, Marking


class Outputs(Enum):
    DFG = "dfg"
    SEQUENCE = "sequence"
    PARALLEL = "parallel"
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"
    ACTIVITIES = "activities"
    SKIPPABLE = "skippable"
    ACTIVITIES_ALWAYS_HAPPENING = "activities_always_happening"
    MIN_TRACE_LENGTH = "min_trace_length"
    TRACE = "trace"


def findsubsets(s, n):
    return list(itertools.combinations(s, n))


def apply(net: PetriNet, im: Marking, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discovers a footprint object from a Petri net

    Parameters
    --------------
    net
        Petri net
    im
        Initial marking
    parameters
        Parameters of the algorithm

    Returns
    --------------
    footprints_obj
        Footprints object
    """
    if parameters is None:
        parameters = {}

    incoming_transitions, outgoing_transitions, eventually_enabled = reachability_graph.marking_flow_petri(net, im,
                                                                                                           return_eventually_enabled=True,
                                                                                                           parameters=parameters)

    sequence = set()

    s1 = set()
    s2 = set()

    for m in outgoing_transitions:
        input_trans = set(x for x in incoming_transitions[m] if x.label is not None)
        output_trans = set(x for x in outgoing_transitions[m].keys() if x.label is not None)
        ev_en = set(x for x in eventually_enabled[m])
        two_sets = findsubsets(output_trans, 2)

        for (x, y) in two_sets:
            s1.add((x, y))
            s1.add((y, x))

        for t1 in input_trans:
            for t2 in ev_en:
                sequence.add((t1, t2))
            for t2 in output_trans:
                s2.add((t1, t2))

    parallel = {(x, y) for (x, y) in s2 if (y, x) in s2 and (x, y) in s1}
    sequence = {(x, y) for (x, y) in sequence if not (x, y) in parallel}

    parallel = {(x.label, y.label) for (x, y) in parallel}
    sequence = {(x.label, y.label) for (x, y) in sequence}

    par_els = {(x[0], x[1]) for x in sequence if (x[1], x[0]) in sequence}
    for el in par_els:
        parallel.add(el)
        sequence.remove(el)

    activities = set(x.label for x in net.transitions if x.label is not None)
    start_activities = set(x.label for x in eventually_enabled[im])

    return {Outputs.SEQUENCE.value: sequence, Outputs.PARALLEL.value: parallel, Outputs.ACTIVITIES.value: activities, Outputs.START_ACTIVITIES.value: start_activities}
