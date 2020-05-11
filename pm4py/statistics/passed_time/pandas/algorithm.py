from pm4py.statistics.passed_time.pandas.versions import pre, post, prepost
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    PRE = pre
    POST = post
    PREPOST = prepost


VERSIONS = {Variants.PRE, Variants.POST, Variants.PREPOST}


def apply(df, activity, variant=Variants.PRE, parameters=None):
    """
    Gets statistics on execution times of the paths to/from the activity

    Parameters
    ------------
    df
        Dataframe
    activity
        Activity
    variant
        Variant:
            - Variants.PRE
            - Variants.POST
            - Variants.PREPOST
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    dictio
        Dictio containing the times from/to the activity
    """
    return exec_utils.get_variant(variant).apply(df, activity, parameters=parameters)
