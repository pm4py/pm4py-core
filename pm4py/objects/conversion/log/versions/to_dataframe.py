import pandas as pd

from pm4py.objects.log import log as log_instance
from pm4py.objects.conversion.log.variants import to_event_stream
import deprecation


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='use objects.conversion.log.variants.to_data_frame')
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


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='use objects.conversion.log.variants.to_data_frame')
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
    if isinstance(log, pd.core.frame.DataFrame):
        return log
    if type(log) is log_instance.EventLog:
        log = to_event_stream.__transform_event_log_to_event_stream(log)
    transf_log = [dict(x) for x in log]
    df = pd.DataFrame.from_dict(transf_log)

    return df
