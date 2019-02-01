import ciso8601
import os

from pm4py.objects import log as log_lib
from pm4py.objects.log.util import sorting


def import_log(filename, parameters=None):
    """
    Import a log object from a XML file
    containing the traces, the events and the simple attributes of them

    Parameters
    -----------
    filename
        XES file to parse
    parameters
        Parameters of the algorithm, including
            timestamp_sort -> Specify if we should sort log by timestamp
            timestamp_key -> If sort is enabled, then sort the log by using this key
            reverse_sort -> Specify in which direction the log should be sorted
            index_trace_indexes -> Specify if trace indexes should be added as event attribute for each event
            max_no_traces_to_import -> Specify the maximum number of traces to import from the log
            (read in order in the XML file)

    Returns
    -----------
    xes
        XES file
    """
    if parameters is None:
        parameters = {}

    timestamp_sort = False
    timestamp_key = "time:timestamp"
    reverse_sort = False
    insert_trace_indexes = False
    max_no_traces_to_import = 1000000000
    skip_bytes = 0
    max_bytes_to_read = 100000000000

    if "timestamp_sort" in parameters:
        timestamp_sort = parameters["timestamp_sort"]
    if "timestamp_key" in parameters:
        timestamp_key = parameters["timestamp_key"]
    if "reverse_sort" in parameters:
        reverse_sort = parameters["reverse_sort"]
    if "insert_trace_indexes" in parameters:
        insert_trace_indexes = parameters["insert_trace_indexes"]
    if "max_no_traces_to_import" in parameters:
        max_no_traces_to_import = parameters["max_no_traces_to_import"]
    if "max_bytes_to_read" in parameters:
        max_bytes_to_read = parameters["max_bytes_to_read"]

    file_size = os.stat(filename).st_size

    if file_size > max_bytes_to_read:
        skip_bytes = file_size - max_bytes_to_read

    log = log_lib.log.EventLog()
    tracecount = 0
    trace = None
    event = None

    f = open(filename, "r")
    f.seek(skip_bytes)

    for line in f:
        content = line.split("\"")
        if len(content) > 0:
            tag = content[0].split("<")[-1]
            if trace is not None:
                if event is not None:
                    if len(content) == 5:
                        if tag.startswith("string"):
                            event[content[1]] = content[3]
                        elif tag.startswith("date"):
                            event[content[1]] = ciso8601.parse_datetime(content[3])
                        elif tag.startswith("int"):
                            event[content[1]] = int(content[3])
                        elif tag.startswith("float"):
                            event[content[1]] = float(content[3])
                        else:
                            event[content[1]] = content[3]
                    elif tag.startswith("/event"):
                        trace.append(event)
                        event = None
                elif tag.startswith("event"):
                    event = log_lib.log.Event()
                elif len(content) == 5:
                    if tag.startswith("string"):
                        trace.attributes[content[1]] = content[3]
                    elif tag.startswith("date"):
                        trace.attributes[content[1]] = ciso8601.parse_datetime(content[3])
                    elif tag.startswith("int"):
                        trace.attributes[content[1]] = int(content[3])
                    elif tag.startswith("float"):
                        trace.attributes[content[1]] = float(content[3])
                    else:
                        trace.attributes[content[1]] = content[3]
                elif tag.startswith("/trace"):
                    log.append(trace)
                    tracecount += 1
                    if tracecount > max_no_traces_to_import:
                        break
                    trace = None
            elif tag.startswith("trace"):
                trace = log_lib.log.Trace()
    f.close()

    if timestamp_sort:
        log = sorting.sort_timestamp(log, timestamp_key=timestamp_key, reverse_sort=reverse_sort)
    if insert_trace_indexes:
        log.insert_trace_index_as_event_attribute()

    return log
