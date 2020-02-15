from pm4py.statistics.traces.pandas import case_statistics


def get_variants_set(df, parameters=None):
    """
    Gets the set of variants from the current dataframe

    Parameters
    --------------
    df
        Dataframe
    parameters
        Possible parameters of the algorithm, including:
            activity_key -> Column that contains the activity

    Returns
    --------------
    variants_set
        Set of variants in the log
    """
    if parameters is None:
        parameters = {}
    var_stats = case_statistics.get_variant_statistics(df, parameters=parameters)
    return set(x["variant"] for x in var_stats)
