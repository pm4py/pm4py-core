from pm4py.log.exporter.csv.versions import pandas_csv_exp

def export_log(log, outputFilePath):
    """
    Exports the given log to CSV format

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        Event log. Also, can take a trace log and convert it to event log
    outputFilePath:
        Output file path
    """

    return pandas_csv_exp.export_log(log, outputFilePath)