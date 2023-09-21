import pandas as pd
import networkx as nx

from copy import deepcopy

def post_processing_nestings(dcr):
    events = deepcopy(dcr['events'])
    rel_matrices = {}
    ind = pd.Index(sorted(events), dtype=str)
    rels = ['conditionsFor']
    for rel in rels:
        rel_matrix = pd.DataFrame(0, columns=ind, index=ind, dtype=int)
        for e in events:
            for e_prime in events:
                if e in dcr[rel] and e_prime in dcr[rel][e]:
                    rel_matrix.at[e, e_prime] = 1
        rel_matrices[rel] = rel_matrix
    relations_to_remove = {}
    new_events = set()
    relations_to_add = {}
    nestings = {}
    nesting_of = {}
    i = 0
    for rel in rels:
        new_nestings_found = True
        G = nx.from_pandas_adjacency(rel_matrices[rel], create_using=nx.DiGraph)
        relations_to_remove[rel] = {}
        relations_to_add[rel] = {}
        while new_nestings_found:
            new_arrows = set()
            new_nodes = set()
            arrows_to_remove = set()
            largest_nesting = {}
            for e in events:
                largest_nesting[e] = 0
            for e in G.nodes:
                for e_prime in G.nodes:
                    if e != e_prime:
                        cin = common_in_neighbors(G, e, e_prime)
                        cin.discard(e)
                        cin.discard(e_prime)
                        con = common_out_neighbors(G, e, e_prime)
                        con.discard(e)
                        con.discard(e_prime)
                        if rel.endswith('For'):
                            con = set()
                        else:
                            cin = set()
                        if len(cin) > 0 or len(con) > 0:
                            if len(cin) > 0:
                                for c in cin:
                                    largest_nesting[c] += 1
                            if len(con) > 0:
                                for c in con:
                                    largest_nesting[c] += 1
            if max(largest_nesting.values()) > 0:
                e = max(largest_nesting, key=largest_nesting.get)
                suc_e = set(G.successors(e))
                pred_e = set(G.predecessors(e))
                if len(suc_e) > 1:
                    proceed = True
                    replace_in = None
                    for k, v in nestings.items():
                        intersect = v.intersection(suc_e)
                        if 0 < len(intersect) < len(suc_e):
                            for s in intersect:
                                arrows_to_remove.add((e, s))
                            proceed = False
                        elif len(intersect) == len(suc_e):
                            replace_in = k
                    if proceed:
                        if suc_e not in nestings.values():
                            nestings[f'N{i}'] = suc_e
                            nesting_of[frozenset(suc_e)] = f'N{i}'
                            new_events.add(f'N{i}')
                            new_nodes.add(f'N{i}')
                            new_arrows.add((e, f'N{i}'))
                            if replace_in:
                                nestings[replace_in] = nestings[replace_in].difference(suc_e)
                                nestings[replace_in].add(f'N{i}')
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
                        if 0 < len(intersect) < len(pred_e):
                            for p in intersect:
                                arrows_to_remove.add((p, e))
                            proceed = False
                    if proceed:
                        if pred_e not in nestings.values():
                            nestings[f'N{i}'] = pred_e
                            nesting_of[frozenset(pred_e)] = f'N{i}'
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
    nesting_dcr['nestings'].update(nestings)
    # when 2, 3 or 4 different relations have the same events then merge the two nestings
    # chain of conditions with self excludes and responses: those are candidates for petri nets to_petri_net
    # or create a subprocess to highlight this as an activity
    return nesting_dcr


def common_out_neighbors(g, i, j):
    return set(g.successors(i)).intersection(g.successors(j))


def common_in_neighbors(g, i, j):
    return set(g.predecessors(i)).intersection(g.predecessors(j))

