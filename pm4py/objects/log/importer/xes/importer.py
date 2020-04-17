from pm4py.objects.log.importer.xes.versions import iterparse_xes, python_nonstandard
from pm4py.objects.log.util import string_to_file
from pm4py.objects.log.util import compression

ITERPARSE = "iterparse"
NONSTANDARD = "nonstandard"

VERSIONS = {ITERPARSE: iterparse_xes.import_log, NONSTANDARD: python_nonstandard.import_log}


def import_log_from_string(log_string, parameters=None, variant=ITERPARSE):
    """
    Imports a log from a string

    Parameters
    -----------
    log_string
        String that contains the XES
    parameters
        Parameters of the algorithm, including
            timestamp_sort -> Specify if we should sort log by timestamp
            timestamp_key -> If sort is enabled, then sort the log by using this key
            reverse_sort -> Specify in which direction the log should be sorted
            index_trace_indexes -> Specify if trace indexes should be added as event attribute for each event
            max_no_traces_to_import -> Specify the maximum number of traces to import from the log
            (read in order in the XML file)
    variant
        Variant of the algorithm to use, including:
            iterparse, nonstandard

    Returns
    -----------
    log
        Trace log object
    """
    temp_file = string_to_file.import_string_to_temp_file(log_string, "xes")
    return import_log(temp_file, parameters=parameters, variant=variant)


def import_log(path, parameters=None, variant=ITERPARSE):
    """
    Import a XES log into a EventLog object

    Parameters
    -----------
    path
        Log path
    parameters
        Parameters of the algorithm, including
            timestamp_sort -> Specify if we should sort log by timestamp
            timestamp_key -> If sort is enabled, then sort the log by using this key
            reverse_sort -> Specify in which direction the log should be sorted
            index_trace_indexes -> Specify if trace indexes should be added as event attribute for each event
            max_no_traces_to_import -> Specify the maximum number of traces to import from the log
            (read in order in the XML file)
    variant
        Variant of the algorithm to use, including:
            iterparse, nonstandard

    Returns
    -----------
    log
        Trace log object
    """
    if path.endswith("gz"):
        path = compression.decompress(path)

    return VERSIONS[variant](path, parameters=parameters)


def apply(path, parameters=None, variant=ITERPARSE):
    """
    Import a XES log into a EventLog object

    Parameters
    -----------
    path
        Log path
    parameters
        Parameters of the algorithm, including
            timestamp_sort -> Specify if we should sort log by timestamp
            timestamp_key -> If sort is enabled, then sort the log by using this key
            reverse_sort -> Specify in which direction the log should be sorted
            index_trace_indexes -> Specify if trace indexes should be added as event attribute for each event
            max_no_traces_to_import -> Specify the maximum number of traces to import from the log
            (read in order in the XML file)
    variant
        Variant of the algorithm to use, including:
            iterparse, nonstandard

    Returns
    -----------
    log
        Trace log object
    """
    return import_log(path, parameters=parameters, variant=variant)
