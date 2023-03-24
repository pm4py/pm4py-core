import numpy as np

rels = ['conditionsFor', 'milestonesFor','responseTo', 'includesTo', 'excludesTo']

def get_simplicity(dcr):
    relation_count = 0
    for k, e1s in dcr.items():
        if k in rels:
            for e1, e2s in e1s.items():
                relation_count = relation_count + len(e2s)

    return relation_count

def get_objective_simplicity(dcr):
    # assume every event is connected to every other event by exactly 1 relation and there are no self-relations
    # this is equivalent to taking all possible combinations of 2 events
    l_events = len(dcr['events'])
    return np.math.comb(l_events, 2)

def get_relative_simplicity(reference_dcr, evaluated_dcr, percent=True):
    benchmark = get_simplicity(reference_dcr)
    to_compare = get_simplicity(evaluated_dcr)
    if percent:
        return (to_compare*100)/benchmark
    else:
        return to_compare/benchmark
