from numpy.random import choice


def pick_transition(et, smap):
    """
    Pick a transition in a set of transitions based on the weights
    specified by the stochastic map

    Parameters
    --------------
    et
        Enabled transitions
    smap
        Stochastic map

    Returns
    --------------
    trans
        Transition chosen according to the weights
    """
    wmap = {ct: smap[ct].get_weight() if ct in smap else 1.0 for ct in et}
    wmap_sv = sum(wmap.values())
    list_of_candidates = []
    probability_distribution = []
    for ct in wmap:
        list_of_candidates.append(ct)
        probability_distribution.append(wmap[ct] / wmap_sv)
    ct = list(choice(et, 1, p=probability_distribution))[0]
    return ct
