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

from pm4py.objects.petri_net.utils.align_utils import levenshtein, discountedEditDistance
from pm4py.objects.petri_net.utils.petri_utils import decorate_places_preset_trans, decorate_transitions_prepostset
from pm4py.objects.petri_net.utils import align_utils as utils
from pm4py.util import exec_utils
from copy import copy
from enum import Enum
from pm4py.statistics.variants.log import get as variants_module



'''
This algorithm computes discounted anti-alignment and brings a precision of process model
See the paper "An A*-Algorithm for Computing Discounted Anti-Alignments in Process Mining" for more details
It is inspired by the verison of the dijkstra_no_heuristic.py for alignment algorithm. 
Author: Boltenhagen Mathilde, Thomas Chatain, Josep Carmona
Date: Jan. 2021
'''


class Parameters(Enum):
    MARKING_LIMIT = "marking_limit"
    EXPONENT = "exponent"
    EPSILON = "epsilon"


def apply(log, petri_net, ini, fin, parameters=None):
    """
    This function is a preliminary function for __search of the discounted algorihtm for AA.
    The function gets the parameters and launches the algorithm on the variants (all traces aren't usefull for AA, see paper).
    """

    # get variants
    variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)
    variants = []
    for index_variant, var in enumerate(variants_idxs):
        variants.append(var.split(","))

    # get the number of times we can reach the same marking, very usefull for choices and loops
    marking_limit =  exec_utils.get_param_value(Parameters.MARKING_LIMIT, parameters, None)
    if marking_limit is None:
        marking_limit=100000

    # the discounted parameter
    exponent = exec_utils.get_param_value(Parameters.EXPONENT, parameters, None)
    if exponent is None:
        exponent=2

    # limit search of very long run see paper "Anti-Alignments -- Measuring The Precision of Process Models and Event Logs"
    epsilon = exec_utils.get_param_value(Parameters.EPSILON, parameters, None)
    if epsilon is None:
        epsilon=0.005

    return __search(petri_net, ini, fin, variants, marking_limit=marking_limit, exponent=exponent,epsilon=epsilon)


def __search(net, ini, fin, variants,  exponent=2, marking_limit=1000, epsilon = 0.005):
    '''
    Launches the A* algorithm to get an Anti-alignment and the precision.
    Notice that this algorithm gives an approximation (lower bound for precision) of AA.
    This function is only called by the previous apply function.
    '''

    decorate_transitions_prepostset(net)
    decorate_places_preset_trans(net)

    mymemory={}
    closed = {}

    ini_state = utils.DijkstraSearchTupleForAntiAndMulti(0, ini, [])
    open_set = [ini_state]
    heapq.heapify(open_set)
    visited = 0
    queued = 0
    traversed = 0
    best, sizeAA = None, None

    distanceTime = 0
    trans_empty_preset = set(t for t in net.transitions if len(t.in_arcs) == 0)

    def costfunction(t, curr_aa, withFrac=True):
        '''
        Computes the discounted cost for current prefix AA + new transition t and the variants.
        :param t: next possible transition
        :param curr_aa: current prefix of run
        :param withFrac: the fraction that prevents the best suffice, this parameter is false at the end of the algorithm.
        :return: the minimal distance of the prefix to the variants
        '''
        if t is None :
            str_aa = [a.label for a in curr_aa]
        elif len(curr_aa)==0 :
            str_aa = [t.label]
        else :
            str_aa = [a.label for a in curr_aa] + [t.label]

        all= []
        for v in variants:
            if str(v+str_aa) not in mymemory.keys() or not withFrac:
                size_of_alignment, distance = discountedEditDistance(str_aa,v, exponent)
                if withFrac:
                    mymemory[str(v+str_aa)] = distance + exponent**(-size_of_alignment)/(exponent-1)
                else :
                    mymemory[str(v+str_aa)] = distance
                mymemory[str(v+str_aa)] = mymemory[str(v+str_aa)]/((1+epsilon)**(len(str_aa)))
            all.append(mymemory[str(v+str_aa)])
        return -min(all)

    # ----------------------------
    # the algorithm starts here
    while not len(open_set) == 0:
        curr = heapq.heappop(open_set)

        if best and  best.g < curr.g:
            continue

        if curr.m == fin:
            curr.g = costfunction(None, curr.r, withFrac=False)

            # in case there only one run
            if not best and (len(heapq.nsmallest(1,open_set))==0 or heapq.nsmallest(1,open_set)[0].g > curr.g):
                return  {'anti-alignment': curr.r, 'cost': curr.g, 'visited_states': visited, 'queued_states': queued,
                         'traversed_arcs': traversed,'precision':getPrecision(curr.r,variants,epsilon)}

            # other runs might be interesting
            elif not best or (best and  best.g > curr.g):
                best = curr
            continue

        closed[curr.m]= 1 if (curr.m) not in closed.keys() else  closed[curr.m]+1

        visited += 1

        possible_enabling_transitions = copy(trans_empty_preset)
        for p in curr.m:
            for t in p.ass_trans:
                possible_enabling_transitions.add(t)

        enabled_trans = [t for t in possible_enabling_transitions if t.sub_marking <= curr.m]
        start=time.time()
        trans_to_visit_with_cost = [(t, costfunction(t,curr.r, withFrac=True)) for t in enabled_trans if t is not None]
        distanceTime+=(time.time()-start)

        for t, cost in trans_to_visit_with_cost:
            traversed += 1
            new_marking = utils.add_markings(curr.m, t.add_marking)

            if ((new_marking) in closed.keys() and closed[new_marking]>marking_limit) or cost==curr.g:
                continue
            queued += 1
            tp = utils.DijkstraSearchTupleForAntiAndMulti(cost, new_marking, curr.r + [t])
            heapq.heappush(open_set, tp)

    return {'anti-alignment': best.r, 'cost': best.g, 'visited_states': visited, 'queued_states': queued,
                      'traversed_arcs': traversed, 'precision': getPrecision(best.r, variants, epsilon)}


def getPrecision(run, variants, epsilon):
    '''
    Once we obtained an AA, we can get the precision of the process model.
    This is computed with the levenshtein edit distance.
    '''
    run = [a.label for a in run]
    all= []
    for v in variants:
        all.append((levenshtein(run,v)/(len(v)+len(run))/(1+epsilon)**(len(run))))
    index_of_min = all.index(min(all))
    precision = 1 - all[index_of_min]
    return precision

