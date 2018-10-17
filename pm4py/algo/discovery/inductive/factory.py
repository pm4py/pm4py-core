from pm4py.algo.discovery.inductive.versions.dfg import dfg_only

INDUCTIVE_ONLY_DFG = 'only_dfg'
VERSIONS = {INDUCTIVE_ONLY_DFG: dfg_only.apply}
VERSIONS_DFG = {INDUCTIVE_ONLY_DFG: dfg_only.apply_dfg}
VERSIONS_TREE = {INDUCTIVE_ONLY_DFG: dfg_only.apply_tree}
VERSIONS_TREE_DFG = {INDUCTIVE_ONLY_DFG: dfg_only.apply_tree_dfg}


def apply(log, parameters=None, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS[variant](log, parameters)


def apply_dfg(dfg, parameters=None, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS_DFG[variant](dfg, parameters)


def apply_tree(log, parameters=None, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS_TREE[variant](log, parameters)


def apply_tree_dfg(dfg, parameters=None, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS_TREE_DFG[variant](dfg, parameters)
