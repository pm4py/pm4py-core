from pm4py.algo.task_mining.grouping.versions import equiv_temp_grouping

EQUIV_TEMP_GROUPING = "equiv_temp_grouping"

VERSIONS = {EQUIV_TEMP_GROUPING: equiv_temp_grouping.apply}


def apply(stream, variant=EQUIV_TEMP_GROUPING, parameters=None):
    """
    Applies a grouping into sentences to a stream

    Parameters
    -------------
    stream
        Event stream
    variant
        Variant of the algorithm to use, possible values:
            - equiv_temp_grouping: Equivalent-columns-or-temporal-grouping algorithm
    parameters
        Parameters of the algorithm, variant specific

    Returns
    -------------
    grouped_stream
        Grouped event stream
    """
    return VERSIONS[variant](stream, parameters=parameters)
