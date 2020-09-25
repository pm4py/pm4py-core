import deprecation

from pm4py.algo.discovery.inductive.versions.im_d import dfg_based

DFG_BASED_OLD_VERSION = 'dfg_based_old_version'
DFG_BASED = 'dfg_based'

DEFAULT_VARIANT = DFG_BASED
DEFAULT_VARIANT_DFG = DFG_BASED

# these variants apply on an EventLog object. Specific conversions are done when needed
# to extract an accepting Petri net
VERSIONS = {DFG_BASED: dfg_based.apply}
# these variants apply on a DFG (dictionary of directly-follows relations along with their count)
# to extract an accepting Petri net
VERSIONS_DFG = {DFG_BASED: dfg_based.apply_dfg}
# these variants apply on an EventLog object. Specific conversions are done when needed
# to extract a process tree
VERSIONS_TREE = {DFG_BASED: dfg_based.apply_tree}
# these variants apply on a DFG (dictionary of directly-follows relations along with their count)
# to extract a process tree
VERSIONS_TREE_DFG = {DFG_BASED: dfg_based.apply_tree_dfg}
# these variants apply on a dictionary/list/set of variants to extract an accepting Petri net
VERSIONS_VARIANTS = {DFG_BASED: dfg_based.apply_variants}
# these variants apply on a dictionary/list/set of variants to extract a process tree
VERSIONS_TREE_VARIANTS = {DFG_BASED: dfg_based.apply_tree_variants}

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (discovery/inductive/factory)')
def apply(log, parameters=None, variant=DEFAULT_VARIANT):
    """
    Apply the IMDF algorithm to a log obtaining a Petri net along with an initial and final marking

    Parameters
    -------------
    log
        Log
    variant
        Variant of the algorithm to apply, possible values:
        - dfg_based: the latest version of the DFG-based algorithm
        - dfg_based_old_version: the previous version of the DFG-based algorithm
    parameters
        Parameters of the algorithm, including:
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> attribute of the log to use as activity name
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
    return VERSIONS[variant](log, parameters=parameters)

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (discovery/inductive/factory)')
def apply_dfg(dfg, parameters=None, variant=DEFAULT_VARIANT_DFG):
    """
    Apply the IMDF algorithm to a DFG graph obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    dfg
        Directly-Follows graph
    variant
        Variant of the algorithm to apply, possible values:
        - dfg_based: the latest version of the DFG-based algorithm
        - dfg_based_old_version: the previous version of the DFG-based algorithm
    parameters
        Parameters of the algorithm, including:
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> attribute of the log to use as activity name
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
    return VERSIONS_DFG[variant](dfg, parameters=parameters)

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (discovery/inductive/factory)')
def apply_tree(log, parameters=None, variant=DEFAULT_VARIANT):
    """
    Apply the IMDF algorithm to a log obtaining a process tree

    Parameters
    ----------
    log
        Log
    variant
        Variant of the algorithm to apply, possible values:
        - dfg_based: the latest version of the DFG-based algorithm
        - dfg_based_old_version: the previous version of the DFG-based algorithm
    parameters
        Parameters of the algorithm, including:
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    ----------
    tree
        Process tree
    """
    return VERSIONS_TREE[variant](log, parameters=parameters)

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (discovery/inductive/factory)')
def apply_tree_dfg(dfg, parameters=None, variant=DEFAULT_VARIANT_DFG):
    """
    Apply the IMDF algorithm to a DFG graph obtaining a process tree

    Parameters
    ----------
    dfg
        Directly-follows graph
    variant
        Variant of the algorithm to apply, possible values:
        - dfg_based: the latest version of the DFG-based algorithm
        - dfg_based_old_version: the previous version of the DFG-based algorithm
    parameters
        Parameters of the algorithm, including:
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    ----------
    tree
        Process tree
    """
    return VERSIONS_TREE_DFG[variant](dfg, parameters=parameters)

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (discovery/inductive/factory)')
def apply_variants(variants, parameters=None, variant=DEFAULT_VARIANT):
    """
    Apply the IMDF algorithm to a dictionary/list/set of variants obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    variants
        Dictionary/list/set of variants in the log
    parameters
        Parameters of the algorithm, including:
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)
    variant
        Variant of the algorithm to apply, possible values:
        - dfg_based: the latest version of the DFG-based algorithm
        - dfg_based_old_version: the previous version of the DFG-based algorithm

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    return VERSIONS_VARIANTS[variant](variants, parameters=parameters)

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (discovery/inductive/factory)')
def apply_tree_variants(variants, parameters=None, variant=DEFAULT_VARIANT):
    """
    Apply the IMDF algorithm to a dictionary/list/set of variants a log obtaining a process tree

    Parameters
    ----------
    variants
        Dictionary/list/set of variants in the log
    parameters
        Parameters of the algorithm, including:
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)
    variant
        Variant of the algorithm to apply, possible values:
        - dfg_based: the latest version of the DFG-based algorithm
        - dfg_based_old_version: the previous version of the DFG-based algorithm

    Returns
    ----------
    tree
        Process tree
    """
    return VERSIONS_TREE_VARIANTS[variant](variants, parameters=parameters)
