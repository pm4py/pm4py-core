from pm4py.log.importer.xes.versions import iterparse_xes, python_nonstandard

ITERPARSE = "iterparse"
NONSTANDARD = "nonstandard"

VERSIONS = {ITERPARSE: iterparse_xes.import_log, NONSTANDARD: python_nonstandard.import_log}

def import_log(path, parameters=None, variant="iterparse"):
    """
    Import a XES log into a TraceLog object

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
            max_no_traces_to_import -> Specify the maximum number of traces to import from the log (read in order in the XML file)

    Returns
    -----------
    log
        Trace log object
    """
    return VERSIONS[variant](path, parameters=parameters)

def apply(logpath, parameters=None, variant="iterparse"):
    """
    Import a XES log into a TraceLog object

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
            max_no_traces_to_import -> Specify the maximum number of traces to import from the log (read in order in the XML file)

    Returns
    -----------
    log
        Trace log object
    """
    return import_log(logpath, parameters=parameters, variant=variant)