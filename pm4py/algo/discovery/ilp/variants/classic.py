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
import numpy as np
from pm4py.util import nx_utils

from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Union, Optional, Dict, Any, Tuple, List
from pm4py.objects.petri_net.obj import PetriNet, Marking
from enum import Enum
from pm4py.util import exec_utils, xes_constants, constants
import warnings
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import filtering_utils
from pm4py.util.lp import solver as lp_solver
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.objects.log.util import artificial
from copy import copy, deepcopy
from pm4py.algo.discovery.causal import algorithm as causal_discovery
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.objects.petri_net.utils import murata
from pm4py.objects.petri_net.utils import reduction
import importlib.util


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    PARAM_ARTIFICIAL_START_ACTIVITY = constants.PARAM_ARTIFICIAL_START_ACTIVITY
    PARAM_ARTIFICIAL_END_ACTIVITY = constants.PARAM_ARTIFICIAL_END_ACTIVITY
    CAUSAL_RELATION = "causal_relation"
    SHOW_PROGRESS_BAR = "show_progress_bar"
    ALPHA = "alpha"


def __transform_log_to_matrix(log: EventLog, activities: List[str], activity_key: str):
    """
    Internal method
    Transforms the event log in a numeric matrix that is used to construct the linear problem.
    """
    matr = []
    for trace in log:
        vect = []
        rep = np.array([0] * len(activities))
        for i in range(len(trace)):
            repi = rep.copy()
            repi[activities.index(trace[i][activity_key])] += 1
            vect.append(repi)
            rep = repi
        matr.append(vect)
    return matr


def __manage_solution(sol, added_places, explored_solutions, net, activities, trans_map):
    """
    Internal method.
    Manages the solution of the linear problem and possibly adds it as a place of the Petri net
    """
    if sol.success:
        sol = lp_solver.get_points_from_sol(sol, variant=lp_solver.SCIPY)
        sol = [round(x) for x in sol]

        if tuple(sol) not in added_places:
            added_places.add(tuple(sol))
            sol = np.array(sol)

            x0 = np.array(sol[:len(activities)])
            y0 = np.array(sol[len(activities):2 * len(activities)])

            if max(x0) > 0 and max(y0) > 0:
                place = PetriNet.Place(str(len(net.places)))
                net.places.add(place)
                i = 0
                while i < len(activities):
                    if sol[i] == 1:
                        petri_utils.add_arc_from_to(trans_map[activities[i]], place, net)
                    i = i + 1
                while i < 2 * len(activities):
                    if sol[i] == 1:
                        petri_utils.add_arc_from_to(place, trans_map[activities[i - len(activities)]], net)
                    i = i + 1
            vec = x0.tolist() + (y0-1).tolist() + [sol[-1]]
            b = sol[-1] - 1 + x0.sum()

            explored_solutions.add((tuple(vec), b))

            return vec, b

    return None, None


def apply(log0: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the ILP miner.

    The implementation follows what is described in the scientific paper:
    van Zelst, Sebastiaan J., et al.
    "Discovering workflow nets using integer linear programming." Computing 100.5 (2018): 529-556.

    Parameters
    ---------------
    log0
        Event log / Event stream / Pandas dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity
        - Parameters.SHOW_PROGRESS_BAR => decides if the progress bar should be shown

    Returns
    ---------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    artificial_start_activity = exec_utils.get_param_value(Parameters.PARAM_ARTIFICIAL_START_ACTIVITY, parameters,
                                                           constants.DEFAULT_ARTIFICIAL_START_ACTIVITY)
    artificial_end_activity = exec_utils.get_param_value(Parameters.PARAM_ARTIFICIAL_END_ACTIVITY, parameters,
                                                         constants.DEFAULT_ARTIFICIAL_END_ACTIVITY)
    show_progress_bar = exec_utils.get_param_value(Parameters.SHOW_PROGRESS_BAR, parameters, constants.SHOW_PROGRESS_BAR)

    log0 = log_converter.apply(log0, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
    log0 = filtering_utils.keep_one_trace_per_variant(log0, parameters=parameters)
    log = artificial.insert_artificial_start_end(deepcopy(log0), parameters=parameters)
    # use the ALPHA causal relation if none is provided as parameter
    causal = exec_utils.get_param_value(Parameters.CAUSAL_RELATION, parameters, causal_discovery.apply(dfg_discovery.apply(log, parameters=parameters)))
    # noise threshold for the sequence encoding graph (when alpha=1, no filtering is applied; when alpha=0, the greatest filtering is applied)
    alpha = exec_utils.get_param_value(Parameters.ALPHA, parameters, 1.0)

    activities = sorted(list(set(x[activity_key] for trace in log for x in trace)))

    # check if the causal relation satisfy the criteria for relaxed sound WF-nets
    G = nx_utils.DiGraph()
    for ca in causal:
        G.add_edge(ca[0], ca[1])

    desc_start = set(nx_utils.descendants(G, artificial_start_activity))
    anc_end = set(nx_utils.ancestors(G, artificial_end_activity))

    if artificial_start_activity in desc_start or artificial_end_activity in anc_end or len(desc_start.union({artificial_start_activity}).difference(activities)) > 0 or len(anc_end.union({artificial_end_activity}).difference(activities)) > 0:
        if constants.SHOW_INTERNAL_WARNINGS:
            warnings.warn("The conditions needed to ensure a relaxed sound WF-net as output are not satisfied.")

    matr = __transform_log_to_matrix(log, activities, activity_key)

    net = PetriNet("ilp")
    im = Marking()
    fm = Marking()
    source = PetriNet.Place("source")
    sink = PetriNet.Place("sink")
    net.places.add(source)
    net.places.add(sink)
    im[source] = 1
    fm[sink] = 1
    trans_map = {}

    # STEP A) construction of the transitions of the Petri net.
    # the source and sink place are connected respectively to the artificial start/end activities
    for act in activities:
        label = act if act not in [artificial_start_activity, artificial_end_activity] else None
        trans_map[act] = PetriNet.Transition(act, label)
        net.transitions.add(trans_map[act])

        if act == artificial_start_activity:
            petri_utils.add_arc_from_to(source, trans_map[act], net)
        elif act == artificial_end_activity:
            petri_utils.add_arc_from_to(trans_map[act], sink, net)

    # STEP B) construction of the sequence encoding graph
    seq_enc_graph = {}
    for j in range(len(matr)):
        trace = matr[j]
        trace_occ = log0[j].attributes["@@num_traces"]
        for i in range(len(trace)):
            prev = -trace[i-1] if i > 0 else np.zeros(len(activities))
            curr = trace[i]
            prev = tuple(prev)
            curr = tuple(curr)
            if prev not in seq_enc_graph:
                seq_enc_graph[prev] = {}
            if curr not in seq_enc_graph[prev]:
                seq_enc_graph[prev][curr] = 0
            seq_enc_graph[prev][curr] += trace_occ
    max_child_seq_enc_graph = {x: max(y.values()) for x, y in seq_enc_graph.items()}

    # STEP C) construction of the base linear problem
    # which will be 'extended' in each step
    c = np.zeros(2*len(activities))
    Aub = []
    bub = []
    Aeq = []
    beq = []

    added_rows_Aub = set()
    added_rows_Aeq = set()

    for trace in matr:
        for i in range(len(trace)):
            row1 = -trace[i-1] if i > 0 else np.zeros(len(activities))
            row2 = trace[i]
            prev = tuple(row1)
            curr = tuple(row2)

            if seq_enc_graph[prev][curr] >= (1-alpha) * max_child_seq_enc_graph[prev]:
                row = row1.tolist() + row2.tolist() + [-1]
                if i < len(trace)-1:
                    if tuple(row) not in added_rows_Aub:
                        added_rows_Aub.add(tuple(row))
                        Aub.append(row)
                        bub.append(0)
                else:
                    if tuple(row) not in added_rows_Aeq:
                        # deviation 1: impose that the place is empty at the end of every trace of the log
                        added_rows_Aeq.add(tuple(row))
                        Aeq.append(row)
                        beq.append(0)

                crow = row2.tolist() + (-row2).tolist()
                c += crow
            else:
                # break not only the current node but all his children
                break

    Aub.append([-1] * (2*len(activities)) + [0])
    bub.append(-1)

    for i in range(2*len(activities)+1):
        row1 = [0] * (2*len(activities)+1)
        row1[i] = -1
        Aub.append(row1)
        bub.append(0)
        row2 = [0] * (2*len(activities)+1)
        row2[i] = 1
        Aub.append(row2)
        bub.append(1)

    # deviation 2: seek only for places that contains initially 0 tokens
    const = [0] * (2 * len(activities)) + [1]
    Aub.append(const)
    bub.append(0)

    c = c.tolist()
    c.append(1)

    integrality = [1] * (2*len(activities)+1)

    ite = 0
    added_places = set()
    explored_solutions = set()

    progress = None
    if importlib.util.find_spec("tqdm") and show_progress_bar and len(causal) > 1:
        from tqdm.auto import tqdm
        progress = tqdm(total=len(causal), desc="discovering Petri net using ILP miner, completed causal relations :: ")

    # STEP D) explore all the causal relations in the log
    # to find places
    for ca in causal:
        Aeq1 = copy(Aeq)
        beq1 = copy(beq)

        const1 = [0] * (2*len(activities) + 1)
        const1[activities.index(ca[0])] = 1
        Aeq1.append(const1)
        beq1.append(1)

        const2 = [0] * (2*len(activities) + 1)
        const2[len(activities) + activities.index(ca[1])] = 1
        Aeq1.append(const2)
        beq1.append(1)

        sol = lp_solver.apply(c, Aub, bub, Aeq1, beq1, variant=lp_solver.SCIPY, parameters={"integrality": integrality})
        __manage_solution(sol, added_places, explored_solutions, net, activities, trans_map)

        ite += 1

        if progress is not None:
            progress.update()

    # gracefully close progress bar
    if progress is not None:
        progress.close()
    del progress


    # here, we also implement the extensive research for places (closing the LP space to previous solutions)
    # as described in the paper (possible STEP D)
    """for tup in explored_solutions:
        Aub.append(list(tup[0]))
        bub.append(tup[1])
    while True:
        sol = lp_solver.apply(c, Aub, bub, Aeq, beq, variant=lp_solver.SCIPY, parameters={"integrality": integrality})

        vec, b = __manage_solution(sol, added_places, explored_solutions, net, activities, trans_map)

        if vec is not None:
            Aub.append(vec)
            bub.append(b)
        ite += 1
        if ite >= 25:
            break"""

    # STEP E) apply the reduction on the implicit places and on the invisible transitions
    net, im, fm = murata.apply_reduction(net, im, fm)
    net = reduction.apply_simple_reduction(net)

    return net, im, fm
