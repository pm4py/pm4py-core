from pm4py.algo.simulation.simple.filtering.pandas.versions import filter_topvariants_soundmodel

TOPVARIANTS_SOUNDMODEL = "topvariants_soundmodel"

VERSIONS = {TOPVARIANTS_SOUNDMODEL: filter_topvariants_soundmodel.apply}


def apply(df, parameters=None, variant=TOPVARIANTS_SOUNDMODEL):
    """
    Apply a filtering algorithm in a simple way in order to provide
    a simple visualization

    Parameters
    -----------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm, including: topvariants_soundmodel

    Returns
    -----------
    filtered_df
        Filtered dataframe
    """
    return VERSIONS[variant](df, parameters=parameters)
