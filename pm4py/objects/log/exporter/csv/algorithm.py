from pm4py.objects.log.exporter.csv.versions import pandas_csv_exp

PANDAS = "pandas"
VERSIONS_STRING = {PANDAS: pandas_csv_exp.export_log_as_string}
VERSIONS = {PANDAS: pandas_csv_exp.export}


def export_log_as_string(log, variant="pandas", parameters=None):
    """
    Factory method to export a CSV from an event log as a string

    Parameters
    -----------
    log
        Event log
    variant
        Selected variant of the algorithm
    parameters
        Parameters of the algorithm

    Returns
    -----------
    string
        String describing the CSV
    """
    return VERSIONS_STRING[variant](log, parameters=parameters)


def export(log, output_file_path, variant="pandas", parameters=None):
    """
    Factory method to export a CSV from an event log

    Parameters
    -----------
    log
        Event log
    output_file_path
        Output file path
    variant
        Selected variant of the algorithm
    parameters
        Parameters of the algorithm
    """
    VERSIONS[variant](log, output_file_path, parameters=parameters)


def apply(log, output_file_path, variant="pandas", parameters=None):
    """
    Factory method to export a CSV from an event log

    Parameters
    -----------
    log
        Event log
    output_file_path
        Output file path
    variant
        Selected variant of the algorithm
    parameters
        Parameters of the algorithm
    """
    export(log, output_file_path, variant=variant, parameters=parameters)


def export_log(log, output_file_path, variant="pandas", parameters=None):
    export(log, output_file_path, variant=variant, parameters=parameters)