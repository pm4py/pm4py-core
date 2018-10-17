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


def export_log_as_string(log, parameters=None):
    """
    Exports the given log to string format

    Parameters
    -----------
    log: :class:`pm4py.log.log.EventLog`
        Event log. Also, can take a trace log and convert it to event log
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    string
        String representing the CSV log
    """
    if parameters is None:
        parameters = {}
    del parameters

    df = get_dataframe_from_log(log)

    return df.to_string()


def export_log(log, output_file_path, parameters=None):
    """
    Exports the given log to CSV format

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        Event log. Also, can take a trace log and convert it to event log
    output_file_path:
        Output file path
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}
    del parameters

    df = get_dataframe_from_log(log)
    df.to_csv(output_file_path)
