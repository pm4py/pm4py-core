from pm4py.algo.discovery.inductive.versions.dfg import dfg_based_old, dfg_based

DFG_BASED_OLD_VERSION = 'dfg_based_old_version'
DFG_BASED = 'dfg_based'

DEFAULT_VARIANT = DFG_BASED
DEFAULT_VARIANT_DFG = DFG_BASED

VERSIONS = {DFG_BASED: dfg_based.apply, DFG_BASED_OLD_VERSION: dfg_based_old.apply}
VERSIONS_DFG = {DFG_BASED: dfg_based.apply_dfg, DFG_BASED_OLD_VERSION: dfg_based_old.apply_dfg}
VERSIONS_TREE = {DFG_BASED: dfg_based.apply_tree, DFG_BASED_OLD_VERSION: dfg_based_old.apply_tree}
VERSIONS_TREE_DFG = {DFG_BASED: dfg_based.apply_tree_dfg, DFG_BASED_OLD_VERSION: dfg_based_old.apply_tree_dfg}
VERSIONS_VARIANTS = {DFG_BASED: dfg_based.apply_variants, DFG_BASED_OLD_VERSION: dfg_based_old.apply_variants}
VERSIONS_TREE_VARIANTS = {DFG_BASED: dfg_based.apply_tree_variants,
                          DFG_BASED_OLD_VERSION: dfg_based_old.apply_tree_variants}


def apply(log, parameters=None, variant=DEFAULT_VARIANT):
    return VERSIONS[variant](log, parameters)


def apply_dfg(dfg, parameters=None, variant=DEFAULT_VARIANT_DFG):
    return VERSIONS_DFG[variant](dfg, parameters)


def apply_tree(log, parameters=None, variant=DEFAULT_VARIANT):
    return VERSIONS_TREE[variant](log, parameters)


def apply_tree_dfg(dfg, parameters=None, variant=DEFAULT_VARIANT_DFG):
    return VERSIONS_TREE_DFG[variant](dfg, parameters)


def apply_variants(variants, parameters=None, variant=DEFAULT_VARIANT):
    return VERSIONS_VARIANTS[variant](variants, parameters)


def apply_tree_variants(variants, parameters=None, variant=DEFAULT_VARIANT):
    return VERSIONS_TREE_VARIANTS[variant](variants, parameters)
