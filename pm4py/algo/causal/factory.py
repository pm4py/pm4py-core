from pm4py.algo.causal import versions as causal_versions

CAUSAL_ALPHA = 'alpha'
CAUSAL_HEURISTIC = 'heuristic'

versions = {CAUSAL_ALPHA: causal_versions.alpha.apply, CAUSAL_HEURISTIC: causal_versions.heuristic.apply}


def apply(dfg, variant=CAUSAL_ALPHA):
    return versions[variant](dfg)





