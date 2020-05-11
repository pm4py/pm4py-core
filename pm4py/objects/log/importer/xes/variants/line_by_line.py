import os
from enum import Enum

from pm4py.objects.log.importer.xes.parameters import Parameters
from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.objects.log.util import sorting
from pm4py.objects.log.util import xes as xes_util
from pm4py.util import parameters as param_util
from pm4py.util.dt_parsing import parser as dt_parser


class Parameters(Enum):
    TIMESTAMP_SORT = False
    TIMESTAMP_KEY = xes_util.DEFAULT_TIMESTAMP_KEY
    REVERSE_SORT = False
    INSERT_TRACE_INDICES = False
    MAX_TRACES = 1000000000
    MAX_BYTES = 10000000000
    SKYP_BYTES = 0


def apply(filename, parameters=None):
    return import_log(filename, parameters)


def __fetch_param_value(param, params):
    return params[param] if param in params else param.value


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
            Parameters.TIMESTAMP_SORT -> Specify if we should sort log by timestamp
            Parameters.TIMESTAMP_KEY -> If sort is enabled, then sort the log by using this key
            Parameters.REVERSE_SORT -> Specify in which direction the log should be sorted
            Parameters.INSERT_TRACE_INDICES -> Specify if trace indexes should be added as event attribute for each event
            Parameters.MAX_TRACES -> Specify the maximum number of traces to import from the log (read in order in the XML file)
            Parameters.MAX_BYTES -> Maximum number of bytes to read
            Parameters.SKYP_BYTES -> Number of bytes to skip


    Returns
    -----------
    xes
        XES file
    """
    if parameters is None:
        parameters = {}

    date_parser = dt_parser.get()
    timestamp_sort = param_util.fetch(Parameters.TIMESTAMP_SORT, parameters)
    timestamp_key = param_util.fetch(Parameters.TIMESTAMP_KEY, parameters)
    reverse_sort = param_util.fetch(Parameters.REVERSE_SORT, parameters)
    insert_trace_indexes = param_util.fetch(Parameters.INSERT_TRACE_INDICES, parameters)
    max_no_traces_to_import = param_util.fetch(Parameters.MAX_TRACES, parameters)
    skip_bytes = param_util.fetch(Parameters.SKYP_BYTES, parameters)
    max_bytes_to_read = param_util.fetch(Parameters.MAX_BYTES, parameters)

    file_size = os.stat(filename).st_size

    if file_size > max_bytes_to_read:
        skip_bytes = file_size - max_bytes_to_read

    log = EventLog()
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
                            event[content[1]] = date_parser.apply(content[3])
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
                    event = Event()
                elif len(content) == 5:
                    if tag.startswith("string"):
                        trace.attributes[content[1]] = content[3]
                    elif tag.startswith("date"):
                        trace.attributes[content[1]] = date_parser.apply(content[3])
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
                trace = Trace()
    f.close()

    if timestamp_sort:
        log = sorting.sort_timestamp(log, timestamp_key=timestamp_key, reverse_sort=reverse_sort)
    if insert_trace_indexes:
        log.insert_trace_index_as_event_attribute()

    return log
