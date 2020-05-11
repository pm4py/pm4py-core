from pm4py.algo.discovery.inductive.versions.dfg import dfg_based_old, dfg_based
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    DFG_BASED = dfg_based


DFG_BASED = Variants.DFG_BASED
DEFAULT_VARIANT = DFG_BASED
DEFAULT_VARIANT_DFG = DFG_BASED

VERSIONS = {Variants.DFG_BASED}


def apply(log, parameters=None, variant=DEFAULT_VARIANT):
    """
    Apply the IMDF algorithm to a log obtaining a Petri net along with an initial and final marking

    Parameters
    -------------
    log
        Log
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.DFG_BASED
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    return exec_utils.get_variant(variant).apply(log, parameters=parameters)


def apply_dfg(dfg, parameters=None, variant=DEFAULT_VARIANT_DFG):
    """
    Apply the IMDF algorithm to a DFG graph obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    dfg
        Directly-Follows graph
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.DFG_BASED
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    return exec_utils.get_variant(variant).apply_dfg(dfg, parameters=parameters)


def apply_tree(log, parameters=None, variant=DEFAULT_VARIANT):
    """
    Apply the IMDF algorithm to a log obtaining a process tree

    Parameters
    ----------
    log
        Log
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.DFG_BASED
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    ----------
    tree
        Process tree
    """
    return exec_utils.get_variant(variant).apply_tree(log, parameters=parameters)


def apply_tree_dfg(dfg, parameters=None, variant=DEFAULT_VARIANT_DFG):
    """
    Apply the IMDF algorithm to a DFG graph obtaining a process tree

    Parameters
    ----------
    dfg
        Directly-follows graph
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.DFG_BASED
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    ----------
    tree
        Process tree
    """
    return exec_utils.get_variant(variant).apply_tree_dfg(dfg, parameters=parameters)


def apply_variants(variants, parameters=None, variant=DEFAULT_VARIANT):
    """
    Apply the IMDF algorithm to a dictionary/list/set of variants obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    variants
        Dictionary/list/set of variants in the log
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.DFG_BASED
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    return exec_utils.get_variant(variant).apply_variants(variants, parameters=parameters)


def apply_tree_variants(variants, parameters=None, variant=DEFAULT_VARIANT):
    """
    Apply the IMDF algorithm to a dictionary/list/set of variants a log obtaining a process tree

    Parameters
    ----------
    variants
        Dictionary/list/set of variants in the log
    variant
        Variant of the algorithm to apply, possible values:
        - Variants.DFG_BASED
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name (default concept:name)

    Returns
    ----------
    tree
        Process tree
    """
    return exec_utils.get_variant(variant).apply_tree_variants(variants, parameters=parameters)
