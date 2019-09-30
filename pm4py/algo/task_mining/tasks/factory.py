from pm4py.algo.task_mining.tasks.versions import equiv_spatial_grouping

EQUIV_SPATIAL_GROUPING = "equiv_spatial_grouping"

VERSIONS = {EQUIV_SPATIAL_GROUPING: equiv_spatial_grouping.apply}


def apply(stream, variant=EQUIV_SPATIAL_GROUPING, parameters=None):
    """
    Applies a grouping based on a set of equivalence columns and the distance between the clicks,
    in order to give eventually a label to each click

    Parameters
    ---------------
    grouped_stream
        Stream of events grouped (possibly, by resource and temporal constraints)
    variant
        Variant of the algorithm to use, possible values: equiv_spatial_grouping
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    new_grouped_stream
        New grouped stream
    all_labels
        All labels indexed
    """
    return VERSIONS[variant](stream, parameters=parameters)
