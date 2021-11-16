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
from pm4py.objects.petri_net.utils.align_utils import  levenshtein, discountedEditDistance
from pm4py.objects.petri_net.utils.petri_utils import  decorate_places_preset_trans,  decorate_transitions_prepostset
from pm4py.objects.petri_net.utils import align_utils as utils
from pm4py.util import exec_utils
from copy import copy
from enum import Enum
from pm4py.statistics.variants.log import get as variants_module

'''
This algorithm computes discounted multi-alignment. 
More details in Boltenhagen's thesis 
Author: Author: Boltenhagen Mathilde, Thomas Chatain, Josep Carmona
Date: Jan. 2021
'''

class Parameters(Enum):
    MARKING_LIMIT = "marking_limit"
    EXPONENT = "exponent"


def apply(log, petri_net, ini, fin, parameters=None):
    """
    This function is a preliminary function for __search of the dijkstra_exponential_heuristic for multi-alignment.
    The function gets the parameters and launches the algorithm on the variants (all traces aren't usefull for MA, see Boltenhagen's thesis).
    """

    # get variants
    variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)
    variants = []
    for index_variant, var in enumerate(variants_idxs):
        variants.append(var.split(","))

    # get the number of times we can reach the same marking, very usefull for concurrency and loops
    marking_limit =  exec_utils.get_param_value(Parameters.MARKING_LIMIT, parameters, None)
    if marking_limit is None:
        marking_limit=100000

    # the discounted parameter
    exponent = exec_utils.get_param_value(Parameters.EXPONENT, parameters, None)
    if exponent is None:
        exponent=2

    return __search(petri_net, ini, fin, variants,  marking_limit=marking_limit, exponent=exponent)


def __search(net, ini, fin, variants, exponent=2, marking_limit=1000):
    '''
    This function is the A* algorithm for multi-alignments.
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

    def costfunction(t, curr_ma, withFrac=True):
        '''
        Compute the maximal distance of the current multi-alignment + t and the variants.
        :param t: transition that we want to add in the current multi-alignment
        :param curr_ma: current prefix of multi-alignment
        :param withFrac: the fraction that prevents the best suffice, this parameter is false at the end of the algorithm.
        '''
        if t is None :
            str_aa = [a.label for a in curr_ma]
        elif len(curr_ma)==0 :
            str_aa = [t.label]
        else :
            str_aa = [a.label for a in curr_ma] + [t.label]

        all= []
        for v in variants:
            if str(v+str_aa) not in mymemory.keys() or not withFrac:
                size_of_alignment, distance = discountedEditDistance(str_aa,v, exponent)
                if withFrac:
                    mymemory[str(v+str_aa)] = distance - (exponent**(-len(str_aa)+1)-exponent**(-(len(str_aa)+len(v))))/(exponent-1)
                else :
                    mymemory[str(v+str_aa)] = distance
            all.append(mymemory[str(v+str_aa)])
        return max(all)

    # ----------------------------
    # a* algorithm starts here
    while not len(open_set) == 0:
        curr = heapq.heappop(open_set)

        if best and  best.g < curr.g:
            continue

        if curr.m == fin:
            curr.g = costfunction(None, curr.r, withFrac=False)
            # in case there only one run
            if not best and (len(heapq.nsmallest(1,open_set))==0 or heapq.nsmallest(1,open_set)[0].g > curr.g):
                return  {'multi-alignment': curr.r, 'cost': curr.g, 'visited_states': visited, 'queued_states': queued,
                         'traversed_arcs': traversed, "max_distance_to_log":getMaxDist(curr.r,variants)}

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
        trans_to_visit_with_cost = [(t, costfunction(t,curr.r, withFrac=True)) for t in enabled_trans if t is not None]

        for t, cost in trans_to_visit_with_cost:
            traversed += 1
            new_marking = utils.add_markings(curr.m, t.add_marking)

            if ((new_marking) in closed.keys() and closed[new_marking]>marking_limit) or cost==curr.g:
                continue
            queued += 1
            tp = utils.DijkstraSearchTupleForAntiAndMulti(cost, new_marking, curr.r + [t])
            heapq.heappush(open_set, tp)

    return  {'multi-alignment': best.r, 'cost': best.g, 'visited_states': visited, 'queued_states': queued,
             'traversed_arcs': traversed, "max_distance_to_log":getMaxDist(best.r,variants)}

def getMaxDist(run, variants):
    '''
    We give the maximal levenshtein edit distance to the variants
    '''
    run = [a.label for a in run]
    all= []
    for v in variants:
        all.append(levenshtein(run,v))
    return max(all)