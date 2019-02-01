from pm4py.objects.log.importer.csv.versions import pandas_df_imp
from pm4py.objects.log.util import string_to_file

PANDAS = "pandas"
VERSIONS = {PANDAS: pandas_df_imp.import_event_stream}


def import_log_from_string(log_string, parameters=None, variant="pandas"):
    """
    Import a CSV log from a string

    Parameters
    -----------
    log_string
        String that contains the CSV
    parameters
        Parameters of the algorithm, including
            sep -> column separator
            quotechar -> (if specified) Character that starts/end big strings in CSV
            nrows -> (if specified) Maximum number of rows to read from the CSV
            sort -> Boolean value that tells if the CSV should be ordered
            sort_field -> If sort option is enabled, then the CSV is automatically sorted by the specified column
    variant
        Variant of the algorithm to use, including:
            pandas

    Returns
    -----------
    log
        Event log object
    """
    temp_file = string_to_file.import_string_to_temp_file(log_string, "csv")
    return import_event_stream(temp_file, parameters=parameters, variant=variant)


def import_event_stream(path, parameters=None, variant="pandas"):
    """
    Import a CSV log into an EventLog object

    Parameters
    -----------
    path
        Log path
    parameters
        Parameters of the algorithm, including
            sep -> column separator
            quotechar -> (if specified) Character that starts/end big strings in CSV
            nrows -> (if specified) Maximum number of rows to read from the CSV
            sort -> Boolean value that tells if the CSV should be ordered
            sort_field -> If sort option is enabled, then the CSV is automatically sorted by the specified column
    variant
        Variant of the algorithm to use, including:
            pandas

    Returns
    -----------
    log
        Event log object
    """
    return VERSIONS[variant](path, parameters=parameters)


def import_event_log(path, parameters=None, variant="pandas"):
    return import_event_stream(path, parameters=parameters, variant="pandas")


def apply(path, parameters=None, variant="pandas"):
    """
    Import a CSV log into an EventLog object

    Parameters
    -----------
    path
        Log path
    parameters
        Parameters of the algorithm, including
            sep -> column separator
            quotechar -> (if specified) Character that starts/end big strings in CSV
            nrows -> (if specified) Maximum number of rows to read from the CSV
            sort -> Boolean value that tells if the CSV should be ordered
            sort_field -> If sort option is enabled, then the CSV is automatically sorted by the specified column
    variant
        Variant of the algorithm to use, including:
            pandas

    Returns
    -----------
    log
        Event log object
    """
    return import_event_stream(path, parameters=parameters, variant=variant)
