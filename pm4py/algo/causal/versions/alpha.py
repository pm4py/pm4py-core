def apply(dfg):
    '''
    Computes a causal graph based on a directly follows graph according to the alpha miner

    Parameters
    ----------
    :param dfg: directly follows relation, should be a dict of the form (activity,activity) -> num of occ.

    Returns
    -------
    :return: dictionary containing all causal relations as keys (with value 1 indicating that it holds)
    '''
    causal_alpha = {}
    for (f, t) in dfg:
        if dfg[(f, t)] > 0:
            if (t, f) not in dfg:
                causal_alpha[(f, t)] = 1
            elif dfg[(t, f)] == 0:
                causal_alpha[(f, t)] = 1
    return causal_alpha