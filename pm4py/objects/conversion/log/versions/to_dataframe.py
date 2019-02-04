import pandas as pd

from pm4py.objects.log import log as log_instance
#from pm4py.objects.conversion.log import factory as log_conv_fact
from pm4py.objects.conversion.log.versions import to_event_stream

def apply(log, parameters=None):
    """
    Return a Pandas dataframe from a given log

    Parameters
    -----------
    log: :class:`pm4py.log.log.EventLog`
        Event log. Also, can take a log and convert it to event stream
    parameters
        Parameters of the algorithm

    Returns
    -----------
    df
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    return get_dataframe_from_event_stream(log)


def get_dataframe_from_event_stream(log):
    """
    Return a Pandas dataframe from a given log

    Parameters
    -----------
    log: :class:`pm4py.log.log.EventLog`
        Event log. Also, can take a log and convert it to event stream

    Returns
    -----------
    df
        Pandas dataframe
    """
    if type(log) is log_instance.EventLog:
        log = to_event_stream.transform_event_log_to_event_stream(log)
    transf_log = [dict(x) for x in log]
    df = pd.DataFrame.from_dict(transf_log)

    return df
