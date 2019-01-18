from pm4py.algo.simulation.simple.model.pandas.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(df, parameters=None, variant=CLASSIC, classic_output=False):
    """
    Gets a simple model out of a Pandas dataframe

    Parameters
    -------------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm to apply (choices: classic)
    classic_output
        Determine if the output shall contains directly the objects (e.g. net, initial_marking, final_marking)
        or can return a more detailed dictionary
    """
    return VERSIONS[variant](df, parameters=parameters, classic_output=classic_output)
