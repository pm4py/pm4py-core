from pm4py.statistics.performance_spectrum.versions import dataframe, log
import pandas as pd

DATAFRAME = "dataframe"
LOG = "log"

VERSIONS = {DATAFRAME: dataframe.apply, LOG: log.apply}


def apply(log, list_activities, parameters=None):
    """
    Finds the performance spectrum provided a log/dataframe
    and a list of activities

    Parameters
    -------------
    log
        Event log/Dataframe
    list_activities
        List of activities interesting for the performance spectrum (at least two)
    parameters
        Parameters of the algorithm, including the activity key and the timestamp key

    Returns
    -------------
    ps
        Performance spectrum object (dictionary)
    """
    from pm4py.objects.conversion.log import factory as log_conv_factory

    if parameters is None:
        parameters = {}

    if len(list_activities) < 2:
        raise Exception("performance spectrum can be applied providing at least two activities!")

    if type(log) is pd.DataFrame:
        points = VERSIONS[DATAFRAME](log, list_activities, parameters)
    else:
        points = VERSIONS[LOG](log_conv_factory.apply(log), list_activities, parameters)

    return points
