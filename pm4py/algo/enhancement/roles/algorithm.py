from pm4py.algo.enhancement.roles.variants import log, pandas
from pm4py.util import exec_utils
from enum import Enum
import pkgutil


class Variants(Enum):
    LOG = log
    PANDAS = pandas


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
        Variant of the algorithm to apply. Possible values:
            - Variants.LOG
            - Variants.PANDAS
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

    if variant is None:
        if pkgutil.find_loader("pandas"):
            import pandas as pd
            if type(log) is pd.DataFrame:
                variant = Variants.PANDAS

        if variant is None:
            variant = Variants.LOG

    return exec_utils.get_variant(variant).apply(log, parameters=parameters)
