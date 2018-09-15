from pm4py.log.importer.xes.versions import iterparse_xes

def import_from_file_xes(filename, timestamp_sort=False, timestamp_key="time:timestamp", reverse_sort=False,
                         insert_trace_indexes=False, max_no_traces_to_import=100000000):
    """
    Imports an XES file into a log object

    Parameters
    ----------
    filename:
        Absolute filename
    timestamp_sort
        Specify if we should sort log by timestamp
    timestamp_key
        If sort is enabled, then sort the log by using this key
    reverse_sort
        Specify in which direction the log should be sorted
    index_trace_indexes
        Specify if trace indexes should be added as event attribute for each event
    max_no_traces_to_import
        Specify the maximum number of traces to import from the log (read in order in the XML file)
    """

    return iterparse_xes.import_from_file_xes(filename, timestamp_sort=timestamp_sort, timestamp_key=timestamp_key, reverse_sort=reverse_sort, insert_trace_indexes=insert_trace_indexes, max_no_traces_to_import=max_no_traces_to_import)