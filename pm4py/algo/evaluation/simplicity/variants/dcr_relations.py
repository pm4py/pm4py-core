import numpy as np
import pandas as pd

variant = "DCR"

rels = ['conditionsFor', 'milestonesFor', 'responseTo', 'includesTo', 'excludesTo']


def simplicity_summary(title, models_to_eval, reference_dcr):
    print(f'{title} \t\t\t\t| Relations|Subprocesses')
    res = pd.DataFrame(columns=['Model', 'Relations', 'Percent', 'Subprocesses'])
    dcr_s = get_simplicity(reference_dcr)
    percent = get_relative_simplicity(reference_dcr, reference_dcr)
    print(f'Reference \t\t|{dcr_s[0]}({percent:.0%})\t|{dcr_s[1]}')
    res = res.append({'Model': 'Reference', 'Relations': dcr_s[0], 'Percent': percent, 'Subprocesses': dcr_s[1]},
                     ignore_index=True)
    i = 1
    for dcr in models_to_eval:
        dcr_s = get_simplicity(dcr)
        percent = get_relative_simplicity(dcr, reference_dcr)
        print(f'Version {i} \t\t|{dcr_s[0]}({percent:.0%})\t|{dcr_s[1]}')
        res = res.append({'Model': f'Version {i}',
                          'Relations': dcr_s[0],
                          'Percent': percent,
                          'Subprocesses': dcr_s[1]}, ignore_index=True)
        i = i + 1

    return res


def get_number_of_edges(dcr):
    relation_count = 0
    for k, e1s in dcr.items():
        if k in rels:
            for e1, e2s in e1s.items():
                relation_count = relation_count + len(e2s)

    return relation_count


def get_number_of_subgraphs(dcr):
    sp_count = 0
    if 'subprocesses' in dcr:
        sp_count = len(dcr['subprocesses'].keys())
    return sp_count


def get_simplicity(dcr, variant="DCR"):
    '''

    Parameters
    ----------
    dcr
    variant

    Returns (no of edges), (no of subprocesses)
    -------

    '''
    relation_count = get_number_of_edges(dcr)
    subprocesses_count = get_number_of_subgraphs(dcr)

    return relation_count, subprocesses_count


def get_objective_simplicity(dcr):
    # assume every event is connected to every other event by exactly 1 relation and there are no self-relations
    # this is equivalent to taking all possible combinations of 2 events
    l_events = len(dcr['events'])
    return np.math.comb(l_events, 2)


def get_relative_simplicity(reference_dcr, evaluated_dcr, percent=False):
    benchmark = get_number_of_edges(reference_dcr)
    to_compare = get_number_of_edges(evaluated_dcr)
    if percent:
        return (to_compare * 100) / benchmark
    else:
        return to_compare / benchmark
