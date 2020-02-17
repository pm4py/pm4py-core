from pm4py.algo.enhancement.roles.common import algorithm
from pm4py.util import xes_constants as xes
from pm4py.util import constants
from collections import Counter


def apply(df, parameters=None):
    """
    Gets the roles (group of different activities done by similar resources)
    out of the log

    Parameters
    -------------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    roles
        List of different roles inside the log
    """
    if parameters is None:
        parameters = {}

    resource_key = parameters[
        constants.PARAMETER_CONSTANT_RESOURCE_KEY] if constants.PARAMETER_CONSTANT_RESOURCE_KEY in parameters else xes.DEFAULT_RESOURCE_KEY
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    activity_resource_couples = Counter(dict(df.groupby([resource_key, activity_key]).size()))

    return algorithm.apply(activity_resource_couples, parameters=parameters)
