
CAUSAL_ALPHA = 'alpha'
CAUSAL_HEURISTIC = 'heuristic'


def compute_causal_relations(dfg, method=CAUSAL_ALPHA):
    methods = {CAUSAL_ALPHA: __compute_alpha,
               CAUSAL_HEURISTIC: __compute_heuristic}
    return methods[method](dfg)


def __compute_alpha(dfg):
    causal_alpha = {}
    for (f, t) in dfg:
        if dfg[(f, t)] > 0:
            if (t, f) not in dfg:
                causal_alpha[(f, t)] = 1
            elif dfg[(t, f)] == 0:
                causal_alpha[(f, t)] = 1
    return causal_alpha


def __compute_heuristic(dfg):
    causal_heur = {}
    for (f, t) in dfg:
        if (f, t) not in causal_heur:
            rev = dfg[(t, f)] if (t, f) in dfg else 0
            causal_heur[(f, t)] = float((dfg[(f, t)] - rev) / (dfg[(f, t)] + rev + 1))
            causal_heur[(t, f)] = -1 * causal_heur[(f, t)]
    return causal_heur
