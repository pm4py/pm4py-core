"""
This module contains code that allows us to compute a causal graph, according to the alpha miner.
It expects a dictionary of the form (activity,activity) -> num of occ.
A causal relation holds between activity a and b, written as a->b, if dfg(a,b) > 0 and dfg(b,a) = 0.
"""


def apply(dfg):
    """
    Computes a causal graph based on a directly follows graph according to the alpha miner

    Parameters
    ----------
    dfg: :class:`dict` directly follows relation, should be a dict of the form (activity,activity) -> num of occ.

    Returns
    -------
    causal_relation: :class:`dict` containing all causal relations as keys (with value 1 indicating that it holds)
    """
    causal_alpha = {}
    for (f, t) in dfg:
        if dfg[(f, t)] > 0:
            if (t, f) not in dfg:
                causal_alpha[(f, t)] = 1
            elif dfg[(t, f)] == 0:
                causal_alpha[(f, t)] = 1
    return causal_alpha
