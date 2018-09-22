from pm4py.algo.discovery.inductive.versions import dfg_only

INDUCTIVE_ONLY_DFG = 'only_dfg'
VERSIONS = {INDUCTIVE_ONLY_DFG: dfg_only.apply}
VERSIONS_DFG = {INDUCTIVE_ONLY_DFG: dfg_only.apply_dfg}

def apply(log, parameters=None, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS[variant](log, parameters)

def apply_dfg(dfg, parameters=None, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS_DFG[variant](dfg, parameters)