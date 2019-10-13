from pm4py.util import constants
from pm4py.objects.log.util import xes


def apply(dataframe, list_activities, parameters):
    """
    Finds the performance spectrum provided a dataframe
    and a list of activities

    Parameters
    -------------
    dataframe
        Dataframe
    list_activities
        List of activities interesting for the performance spectrum (at least two)
    parameters
        Parameters of the algorithm, including the activity key and the timestamp key

    Returns
    -------------
    points
        Points of the performance spectrum
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY

    return None
