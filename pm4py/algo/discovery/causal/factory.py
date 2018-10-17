from pm4py.algo.discovery.causal.versions import alpha, heuristic

CAUSAL_ALPHA = 'alpha'
CAUSAL_HEURISTIC = 'heuristic'

versions = {CAUSAL_ALPHA: alpha.apply, CAUSAL_HEURISTIC: heuristic.apply}


def apply(dfg, variant=CAUSAL_ALPHA):
    return versions[variant](dfg)
