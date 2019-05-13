from pm4py.objects.lifecycle_log.util import get_int_tree_attribute


def apply(log, parameters=None):
    """
    Gets a set of interval trees for a particular attribute (one interval tree per value)
    that aims to show how many intersections (contemporary work) are there for that attribute
    (activity/resource/station ...)

    Parameters
    ------------
    log
        Interval log (if not, it is automatically converted)
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    log
        Possibly transformed log
    dict_int_trees
        Dictionary of interval trees, one for each attribute value
    """
    return get_int_tree_attribute.get_int_tree(log, parameters=parameters)
