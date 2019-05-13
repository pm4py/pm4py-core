from pm4py.algo.other.intervaltree.representation.versions import get_distr_points_interval_tree

CLASSIC = "classic"

VERSIONS = {CLASSIC: get_distr_points_interval_tree.get_distr_points}


def apply(tree, variant=CLASSIC, parameters=None):
    """
    Get the distribution of interval overlapping in the interval tree
    (e.g. a point with 0 intersections has no intervals, a point with 1 intersection
    has 1 corresponding interval, a point with N intersections has N corresponding intervals

    Parameters
    -------------
    tree
        Interval tree
    variant
        Variant of the algorithm (possible value: classic)
    parameters
        Parameters of the algorithm, including:
            n_points => Number of points to represent
    """
    return VERSIONS[variant](tree, parameters=parameters)
