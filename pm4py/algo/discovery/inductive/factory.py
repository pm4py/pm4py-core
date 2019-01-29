from pm4py.algo.discovery.inductive.versions.dfg import imdfa, imdfb

INDUCTIVE_ONLY_DFG = 'only_dfg'
IMDFA = 'imdfa'
IMDFB = 'imdfb'

DEFAULT_VARIANT = IMDFA

VERSIONS = {INDUCTIVE_ONLY_DFG: imdfa.apply, IMDFA: imdfa.apply, IMDFB: imdfb.apply}
VERSIONS_DFG = {INDUCTIVE_ONLY_DFG: imdfa.apply_dfg, IMDFA: imdfa.apply_dfg, IMDFB: imdfb.apply_dfg}
VERSIONS_TREE = {INDUCTIVE_ONLY_DFG: imdfa.apply_tree, IMDFA: imdfa.apply_tree, IMDFB: imdfb.apply_tree}
VERSIONS_TREE_DFG = {INDUCTIVE_ONLY_DFG: imdfa.apply_tree_dfg, IMDFA: imdfa.apply_tree_dfg, IMDFB: imdfb.apply_tree_dfg}


def apply(log, parameters=None, variant=DEFAULT_VARIANT):
    return VERSIONS[variant](log, parameters)


def apply_dfg(dfg, parameters=None, variant=DEFAULT_VARIANT):
    return VERSIONS_DFG[variant](dfg, parameters)


def apply_tree(log, parameters=None, variant=DEFAULT_VARIANT):
    return VERSIONS_TREE[variant](log, parameters)


def apply_tree_dfg(dfg, parameters=None, variant=DEFAULT_VARIANT):
    return VERSIONS_TREE_DFG[variant](dfg, parameters)
