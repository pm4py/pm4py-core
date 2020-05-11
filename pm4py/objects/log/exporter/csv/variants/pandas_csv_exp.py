from pm4py.objects.conversion.log import converter


def __export_log_as_string(log, parameters=None):
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
    df = converter.apply(log, variant=converter.Variants.TO_DATA_FRAME)
    return df.to_string()


def __export(log, output_file_path, parameters=None):
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

    df = converter.apply(log, variant=converter.Variants.TO_DATA_FRAME)
    df.to_csv(output_file_path, index=False)


def apply(log, output_file_path, parameters=None):
    return __export(log, output_file_path, parameters=parameters)
