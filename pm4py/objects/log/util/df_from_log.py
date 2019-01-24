import pandas as pd

from pm4py.objects.log import log as log_instance
from pm4py.objects.log import transform as log_transform


def get_dataframe_from_log(log):
    """
    Return a Pandas dataframe from a given log

    Parameters
    -----------
    log: :class:`pm4py.log.log.EventLog`
        Event log. Also, can take a trace log and convert it to event log

    Returns
    -----------
    df
        Pandas dataframe
    """
    if type(log) is log_instance.TraceLog:
        log = log_transform.transform_trace_log_to_event_log(log)
    transf_log = [dict(x) for x in log]
    df = pd.DataFrame.from_dict(transf_log)

    return df
