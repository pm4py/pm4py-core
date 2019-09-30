from pm4py.algo.task_mining.sequence_mining.versions import prefix_span

PREFIX_SPAN = "prefix_span"

VERSIONS = {PREFIX_SPAN: prefix_span.apply}


def apply(grouped_stream, all_labels, variant=PREFIX_SPAN, parameters=None):
    """
    Applies the prefix span algorithm

    Parameters
    -------------
    grouped_stream
        Grouped stream
    all_labels
        Indexed labels
    variant
        Variant of the algorithm to use, possible values: prefix_span
    parameters
        All the parameters of the algorithm

    Returns
    --------------
    frequents
        List containing frequent itemsets as label indexes
    frequents_label
        List containing frequent itemsets as labels
    frequents_encodings
        List containing frequent itemsets as word encodings
    frequents_occurrences
        List containing all the sequences of events associated to the corresponding itemset
    """

    return VERSIONS[variant](grouped_stream, all_labels, parameters=parameters)
