from pm4py.algo.enhancement.roles.versions import log, pandas
import pandas as pd

LOG = 'log'
PANDAS = 'pandas'

VERSIONS = {LOG: log.apply, PANDAS: pandas.apply}


def apply(log, variant=None, parameters=None):
    """
    Gets the roles (group of different activities done by similar resources)
    out of the log

    Parameters
    -------------
    log
        Log object (also Pandas dataframe)
    variant
        Variant of the algorithm to apply. Possible values: log, pandas
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    roles
        List of different roles inside the log
    """
    if variant is None:
        if type(log) is pd.DataFrame:
            variant = PANDAS
        else:
            variant = LOG

    return VERSIONS[variant](log, parameters=parameters)
