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
import datetime
import json
from copy import deepcopy
import pandas as pd
import networkx as nx

import pm4py.objects.log.obj
from pm4py.algo.discovery.dcr_discover.variants import discover_basic, discover_subprocess_mutual_exclusion#, discover_subprocess_predecessors, discover_subprocess_given_domain_knowledge
from pm4py.algo.discovery.dcr_discover import time_mining, initial_pending
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Tuple


class Variants(Enum):
    DCR_BASIC = discover_basic
    # DCR_SUBPROCESS_PRE = discover_subprocess_predecessors
    DCR_SUBPROCESS_ME = discover_subprocess_mutual_exclusion
    # DCR_SUBPROCESS_DK = discover_subprocess_given_domain_knowledge


DCR_BASIC = Variants.DCR_BASIC
# DCR_SUBPROCESS_PRE = Variants.DCR_SUBPROCESS_PRE
DCR_SUBPROCESS_ME = Variants.DCR_SUBPROCESS_ME
# DCR_SUBPROCESS_DK = Variants.DCR_SUBPROCESS_DK

VERSIONS = {DCR_BASIC, DCR_SUBPROCESS_ME}#, DCR_SUBPROCESS_PRE, DCR_SUBPROCESS_DK}


def apply(input_log, variant=DCR_BASIC, **parameters):
    """
    Parameters
    -----------
    input_log
    variant
        Variant of the algorithm to use:
            - DCR_BASIC
            - DCR_SUBPROCESS_ME
    parameters
        Algorithm related params
        finaAdditionalConditions: [True or False]
    Returns
    -----------
    dcr graph
    """
    log = deepcopy(input_log)
    if variant.value == Variants.DCR_BASIC.value:
        print('[i] Mining with basic DisCoveR')
        if not isinstance(log, pm4py.objects.log.obj.EventLog):
            log = pm4py.convert_to_event_log(log)
        disc_b = discover_basic.Discover()
        dcr_model, la = disc_b.mine(log, **parameters)
        if 'timed' in parameters.keys() and parameters['timed']:
            dcr_model = apply_timed(dcr_model, log, None)
        if 'pending' in parameters.keys() and parameters['pending']:
            dcr_model = initial_pending.apply(dcr_model, log)
        return dcr_model, la
    elif variant.value == Variants.DCR_SUBPROCESS_ME.value:
        print('[i] Mining with Sp-DisCoveR (ME)')
        dcr_model, sp_log = discover_subprocess_mutual_exclusion.apply(log, **parameters)
        if 'timed' in parameters.keys() and parameters['timed']:
            dcr_model = apply_timed(dcr_model, deepcopy(input_log), sp_log)
        if 'pending' in parameters.keys() and parameters['pending']:
            dcr_model = initial_pending.apply(dcr_model, sp_log)
        dcr_model = post_processing(dcr_model,**parameters)
        return dcr_model, sp_log
    # elif variant.value == Variants.DCR_SUBPROCESS_DK.value:
    #     print('[i] Mining with Sp-DisCoveR (DK)')
    #     dcr_model, sp_log = discover_subprocess_given_domain_knowledge.apply(log, **parameters)
    #     if 'timed' in parameters.keys() and parameters['timed']:
    #         dcr_model = apply_timed(dcr_model, deepcopy(input_log), sp_log)
    #     if 'pending' in parameters.keys() and parameters['pending']:
    #         dcr_model = initial_pending.apply(dcr_model, sp_log)
    #     return dcr_model, sp_log
    # elif variant.value == Variants.DCR_SUBPROCESS_PRE.value:
    #     dcr_model, sp_log = discover_subprocess_predecessors.apply(log, **parameters)
    #     if 'timed' in parameters.keys() and parameters['timed']:
    #         dcr_model = apply_timed(dcr_model, deepcopy(input_log), sp_log)
    #     if 'pending' in parameters.keys() and parameters['pending']:
    #         dcr_model = initial_pending.apply(dcr_model, sp_log)
    #     return dcr_model, sp_log

def post_processing(dcr,nestings = False, timed = True, **parameters):
    # if nestings:
    #     dcr = post_processing_nestings(dcr)
    if timed:
        dcr = post_processing_timed(dcr)
    return dcr

def post_processing_timed(dcr):
    # if there is a timed condition wrap it in a subprocess to still enforce the time
    # we do this due to the way we mine time from the event log which is different from the definition of a
    # delay condition. This delay is observed in all log traces therefore it is more accurate w.r.t. the log
    # to have this delay persist event after the executed event is excluded
    conditions = deepcopy(dcr['conditionsForDelays'])
    for e1, cond_time_dict in conditions.items():
        for e0, time in cond_time_dict.items():
            if time > datetime.timedelta(0):
                new_sp = f'{e0}_ne'  # not excluded
                dcr = replace_events_ne(dcr, e0, new_sp)
                dcr['subprocesses'][new_sp] = set([e0])
    # if there are 2 or more events that have the exact same relations to/from the exact same events
    # then they can be grouped into subprocesses. This can be done iteratively. Discover a subprocess then
    # group that subprocess based on the same rule.
    return dcr

def post_processing_nestings(dcr):
    events = deepcopy(dcr['events'])
    rel_matrices = {}
    ind = pd.Index(sorted(events), dtype=str)
    rels = []#['conditionsFor','responseTo', 'excludesTo', 'includesTo']  # , 'milestonesFor',]
    # edge_weights = pd.DataFrame(0, columns=ind, index=ind, dtype=int)
    for rel in rels:
        rel_matrix = pd.DataFrame(0, columns=ind, index=ind, dtype=int)
        for e in events:
            for e_prime in events:
                if e in dcr[rel] and e_prime in dcr[rel][e]:
                    rel_matrix.at[e, e_prime] = 1
        # edge_weights = edge_weights.add(rel_matrix, fill_value=0)
        rel_matrices[rel] = rel_matrix
    # rel_matrices['all'] = edge_weights
    # for all relations get pairs of nodes that share at least a common successor or predecessor in this adjencency graph
    # nestings_per_rel = {}
    relations_to_remove = {}
    new_events = set()
    relations_to_add = {}
    nestings = {}
    nesting_of = {}
    i = 0
    # dcr = deepcopy(rtfmp_reference_dcr)
    for rel in rels:
        # G = None
        new_nestings_found = True
        # print(f'[i] {rel}')
        # if not G:
        G = nx.from_pandas_adjacency(rel_matrices[rel], create_using=nx.DiGraph)
        relations_to_remove[rel] = {}
        relations_to_add[rel] = {}
        while new_nestings_found:
            new_arrows = set()
            new_nodes = set()
            arrows_to_remove = set()
            largest_nesting = {}
            # sem_for_nestings = semantics_obj.DcrSemantics(dcr)
            for e in events:
                largest_nesting[e] = 0
            # they have to be top level events
            for e in G.nodes:
                for e_prime in G.nodes:
                    if e != e_prime:
                        cin = common_in_neighbors(G, e, e_prime)
                        cin.discard(e)
                        cin.discard(e_prime)
                        # cin = cin.intersection(sem_for_nestings.tl_events)
                        con = common_out_neighbors(G, e, e_prime)
                        con.discard(e)
                        con.discard(e_prime)
                        if rel.endswith('For'):
                            con = set()
                        else:
                            cin = set()
                        # con = con.intersection(sem_for_nestings.tl_events)
                        if len(cin) > 0 or len(con) > 0:
                            if len(cin) > 0:
                                for c in cin:
                                    largest_nesting[c] += 1
                            if len(con) > 0:
                                for c in con:
                                    largest_nesting[c] += 1
                            # print(f'{e} and {e_prime} | cin: {cin} con: {con}')
            if max(largest_nesting.values()) > 0:
                e = max(largest_nesting, key=largest_nesting.get)
                # print(f'[i] Largest nesting: {e} {max(largest_nesting.values())}')
                suc_e = set(G.successors(e))
                pred_e = set(G.predecessors(e))
                # print(f'pred: {pred_e} -> {e} -> {suc_e}')
                if len(suc_e) > 1:
                    proceed = True
                    replace_in = None
                    for k, v in nestings.items():
                        intersect = v.intersection(suc_e)
                        if len(intersect)>0 and len(intersect)<len(suc_e):
                            for s in intersect:
                                arrows_to_remove.add((e, s))
                            proceed = False
                        elif len(intersect) == len(suc_e):
                            replace_in = k
                    if proceed:
                        if suc_e not in nestings.values():
                            nestings[f'N{i}'] = suc_e
                            nesting_of[frozenset(suc_e)] = f'N{i}'
                            # dcr['events'].add(f'N{i}')
                            # dcr['subprocesses'][f'N{i}'] = suc_e
                            new_events.add(f'N{i}')
                            new_nodes.add(f'N{i}')
                            new_arrows.add((e, f'N{i}'))
                            if replace_in:
                                nestings[replace_in] = nestings[replace_in].difference(suc_e)
                                nestings[replace_in].add(f'N{i}')
                                replace_in = None
                            i += 1
                        else:
                            existing_nesting = nesting_of[frozenset(suc_e)]
                            new_arrows.add((e, existing_nesting))
                        for s in suc_e:
                            arrows_to_remove.add((e, s))
                if len(pred_e) > 1:
                    proceed = True
                    for v in nestings.values():
                        intersect = v.intersection(pred_e)
                        if len(intersect)>0 and len(intersect)<len(pred_e):
                            for p in intersect:
                                arrows_to_remove.add((p,e))
                            proceed = False
                    if proceed:
                        if pred_e not in nestings.values():
                            nestings[f'N{i}'] = pred_e
                            nesting_of[frozenset(pred_e)] = f'N{i}'
                            # dcr['events'].add(f'N{i}')
                            # dcr['subprocesses'][f'N{i}'] = pred_e
                            new_events.add(f'N{i}')
                            new_nodes.add(f'N{i}')
                            new_arrows.add((f'N{i}', e))
                            i += 1
                        else:
                            existing_nesting = nesting_of[frozenset(pred_e)]
                            new_arrows.add((e, existing_nesting))
                        for p in pred_e:
                            arrows_to_remove.add((p, e))

                relations_to_remove[rel].update(arrows_to_remove)
                relations_to_add[rel].update(new_arrows)
                for k, v in arrows_to_remove:
                    G.remove_edge(k, v)
                for k in new_nodes:
                    G.add_node(k)
                    events.add(k)
                for k, v in new_arrows:
                    G.add_edge(k, v)
            else:
                new_nestings_found = False
                # print(f'[!] No nestings for rel {rel}')

        # nestings_per_rel[rel] = nestings
    # print(nestings)
    # now optimize the nestings in between the relations
    nesting_dcr = deepcopy(dcr)
    nesting_dcr['events'] = nesting_dcr['events'].union(new_events)
    nesting_dcr['marking']['included'] = nesting_dcr['marking']['included'].union(new_events)
    # for each relation remove the event to event relations and replace them with the event to nesting
    for rel in rels:
        for e, e_prime in relations_to_remove[rel].items():
            nesting_dcr[rel][e].discard(e_prime)
        for e, e_prime in relations_to_add[rel].items():
            if e not in nesting_dcr[rel]:
                nesting_dcr[rel][e] = set([e_prime])
            else:
                nesting_dcr[rel][e].add(e_prime)
        # nesting_dcr['subprocesses'].update(nestings_per_rel[rel])
    nesting_dcr['subprocesses'].update(nestings)
    # when 2, 3 or 4 different relations have the same events then merge the two nestings
    return nesting_dcr
    # chain of conditions with self excludes and responses: those are candidates for petri nets mappings
    # or create a subprocess to highlight this as an activity
    # return dcr

def common_out_neighbors(g, i, j):
    return set(g.successors(i)).intersection(g.successors(j))

def common_in_neighbors(g, i, j):
    return set(g.predecessors(i)).intersection(g.predecessors(j))

def replace_events_ne(dcr,e0,new_sp):
    # new_dcr = {
    #     'events': set(),
    #     'conditionsFor': {},
    #     'milestonesFor': {},
    #     'responseTo': {},
    #     'includesTo': {},
    #     'excludesTo': {},
    #     'marking': {'executed': set(),
    #                 'included': set(),
    #                 'pending': set(),
    #                 'executedTime': {},  # Gives the time since a event was executed
    #                 'pendingDeadline': {}  # The deadline until an event must be executed
    #                 },
    #     'conditionsForDelays': {},
    #     'responseToDeadlines': {},
    #     'subprocesses': {},
    #     'labels': set(),
    #     'labelMapping': {},
    #     'roles': set(),
    #     'roleAssignments': set()
    # }
    new_dcr = deepcopy(dcr)
    new_dcr['events'].add(new_sp)
    for m in ['executed', 'included', 'pending']:
        if e0 in dcr['marking'][m]:
            new_dcr['marking'][m].add(new_sp)
    for k, v in dcr['conditionsFor'].items():
        if e0 in v:
            new_dcr['conditionsFor'][k].discard(e0)
            new_dcr['conditionsFor'][k].add(new_sp)
    for k, v in dcr['conditionsForDelays'].items():
        if e0 in v.keys():
            new_dcr['conditionsForDelays'][k][new_sp] = new_dcr['conditionsForDelays'][k].pop(e0)
    return new_dcr

def apply_timed(dcr_model, log, sp_log):
    timings = time_mining.apply(dcr_model=dcr_model, event_log=log, method='standard', sp_log=sp_log)
    # these should be a dict with events as keys and tuples as values
    if 'conditionsForDelays' not in dcr_model:
        dcr_model['conditionsForDelays'] = {}
    if 'responseToDeadlines' not in dcr_model:
        dcr_model['responseToDeadlines'] = {}
    for timing, value in timings.items():
        if timing[0] == 'CONDITION':
            e1 = timing[2]
            e2 = timing[1]
            if e1 not in dcr_model['conditionsForDelays']:
                dcr_model['conditionsForDelays'][e1] = {}
            dcr_model['conditionsForDelays'][e1][e2] = value
        elif timing[0] == 'RESPONSE':
            e1 = timing[1]
            e2 = timing[2]
            if e1 not in dcr_model['responseToDeadlines']:
                dcr_model['responseToDeadlines'][e1] = {}
            dcr_model['responseToDeadlines'][e1][e2] = value
    return dcr_model
