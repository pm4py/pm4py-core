from pm4py.algo.discovery.inductive.versions.dfg import imdfa

INDUCTIVE_ONLY_DFG = 'only_dfg'
IMDFA = 'imdfa'

VERSIONS = {INDUCTIVE_ONLY_DFG: imdfa.apply, IMDFA: imdfa.apply}
VERSIONS_DFG = {INDUCTIVE_ONLY_DFG: imdfa.apply_dfg, IMDFA: imdfa.apply_dfg}
VERSIONS_TREE = {INDUCTIVE_ONLY_DFG: imdfa.apply_tree, IMDFA: imdfa.apply_tree}
VERSIONS_TREE_DFG = {INDUCTIVE_ONLY_DFG: imdfa.apply_tree_dfg, IMDFA: imdfa.apply_tree_dfg}


def apply(log, parameters=None, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS[variant](log, parameters)


def apply_dfg(dfg, parameters=None, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS_DFG[variant](dfg, parameters)


def apply_tree(log, parameters=None, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS_TREE[variant](log, parameters)


def apply_tree_dfg(dfg, parameters=None, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS_TREE_DFG[variant](dfg, parameters)
