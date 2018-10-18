def apply(dfg):
    """
    Computes a causal graph based on a directly follows graph according to the heuristics miner

    Parameters
    ----------
    dfg: :class:`dict` directly follows relation, should be a dict of the form (activity,activity) -> num of occ.

    Returns
    -------
    :return: dictionary containing all causal relations as keys (with value inbetween -1 and 1 indicating that
    how strong it holds)
    """
    causal_heur = {}
    for (f, t) in dfg:
        if (f, t) not in causal_heur:
            rev = dfg[(t, f)] if (t, f) in dfg else 0
            causal_heur[(f, t)] = float((dfg[(f, t)] - rev) / (dfg[(f, t)] + rev + 1))
            causal_heur[(t, f)] = -1 * causal_heur[(f, t)]
    return causal_heur
