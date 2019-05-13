from pm4py.algo.other.intervaltree.builder.versions import int_tree_attribute

INT_TREE_ATTRIBUTE = "int_tree_attribute"

VERSIONS = {INT_TREE_ATTRIBUTE: int_tree_attribute.apply}


def apply(log, variant=INT_TREE_ATTRIBUTE, parameters=None):
    """
    Gets a set of interval trees from a log, according to the implementation
    of the chosen version

    Parameters
    ------------
    log
        Interval log (if not, it is automatically converted)
    variant
        Variant of the algorithm (possible values: int_tree_attribute)
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    log
        Possibly transformed log
    dict_int_trees
        Dictionary of interval trees
    """
    return VERSIONS[variant](log, parameters=parameters)
