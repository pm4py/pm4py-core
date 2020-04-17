from pm4py.algo.enhancement.roles.versions import log, pandas
import pandas as pd

LOG = 'log'
PANDAS = 'pandas'

DEFAULT_THRESHOLD = 0.65
ROLES_THRESHOLD_PARAMETER = "roles_threshold_parameter"

VERSIONS = {LOG: log.apply, PANDAS: pandas.apply}


def apply(log, variant=None, parameters=None):
    """
    Gets the roles (group of different activities done by similar resources)
    out of the log.

    The roles detection is introduced by
    Burattin, Andrea, Alessandro Sperduti, and Marco Veluscek. "Business models enhancement through discovery of roles." 2013 IEEE Symposium on Computational Intelligence and Data Mining (CIDM). IEEE, 2013.


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
        List of different roles inside the log, including:
        roles_threshold_parameter => threshold to use with the algorithm
    """
    if parameters is None:
        parameters = {}

    if ROLES_THRESHOLD_PARAMETER not in parameters:
        parameters[ROLES_THRESHOLD_PARAMETER] = DEFAULT_THRESHOLD

    if variant is None:
        if type(log) is pd.DataFrame:
            variant = PANDAS
        else:
            variant = LOG

    return VERSIONS[variant](log, parameters=parameters)
