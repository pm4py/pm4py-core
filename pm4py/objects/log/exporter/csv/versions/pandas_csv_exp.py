from pm4py.objects.conversion.log.versions.to_dataframe import get_dataframe_from_event_stream


def export_log_as_string(log, parameters=None):
    """
    Exports the given log to string format

    Parameters
    -----------
    log: :class:`pm4py.log.log.EventLog`
        Event log. Also, can take a log and convert it to event stream
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

    df = get_dataframe_from_event_stream(log)

    return df.to_string()


def export(log, output_file_path, parameters=None):
    """
    Exports the given log to CSV format

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        Event log. Also, can take a log and convert it to event stream
    output_file_path:
        Output file path
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}
    del parameters

    df = get_dataframe_from_event_stream(log)
    df.to_csv(output_file_path, index=False)


def export_log(log, output_file_path, parameters=None):
    return export(log, output_file_path, parameters=parameters)
