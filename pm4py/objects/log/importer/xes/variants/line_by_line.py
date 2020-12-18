import os
import sys
from enum import Enum
from io import StringIO

from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.objects.log.util import sorting
from pm4py.util import constants, xes_constants, exec_utils
from pm4py.util.dt_parsing import parser as dt_parser


class Parameters(Enum):
    TIMESTAMP_SORT = "timestamp_sort"
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    REVERSE_SORT = "reverse_sort"
    MAX_TRACES = "max_traces"
    MAX_BYTES = "max_bytes"
    SKIP_BYTES = "skip_bytes"


def apply(filename, parameters=None):
    return import_log(filename, parameters)


def __fetch_param_value(param, params):
    return params[param] if param in params else param.value


def import_log_from_file_object(f, file_size=sys.maxsize, parameters=None):
    """
    Import a log object from a (XML) file object

    Parameters
    -----------
    f
        file object
    file_size
        Size of the file (measured on disk)
    parameters
        Parameters of the algorithm, including
            Parameters.TIMESTAMP_SORT -> Specify if we should sort log by timestamp
            Parameters.TIMESTAMP_KEY -> If sort is enabled, then sort the log by using this key
            Parameters.REVERSE_SORT -> Specify in which direction the log should be sorted
            Parameters.MAX_TRACES -> Specify the maximum number of traces to import from the log (read in order in the XML file)
            Parameters.MAX_BYTES -> Maximum number of bytes to read
            Parameters.SKYP_BYTES -> Number of bytes to skip


    Returns
    -----------
    log
        Log file
    """
    date_parser = dt_parser.get()

    max_no_traces_to_import = exec_utils.get_param_value(Parameters.MAX_TRACES, parameters, sys.maxsize)
    timestamp_sort = exec_utils.get_param_value(Parameters.TIMESTAMP_SORT, parameters, False)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    reverse_sort = exec_utils.get_param_value(Parameters.REVERSE_SORT, parameters, False)

    skip_bytes = exec_utils.get_param_value(Parameters.SKIP_BYTES, parameters, False)
    max_bytes_to_read = exec_utils.get_param_value(Parameters.MAX_BYTES, parameters, sys.maxsize)

    if file_size > max_bytes_to_read:
        skip_bytes = file_size - max_bytes_to_read

    log = EventLog()
    tracecount = 0
    trace = None
    event = None

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

    if timestamp_sort:
        log = sorting.sort_timestamp(log, timestamp_key=timestamp_key, reverse_sort=reverse_sort)

    return log


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
            Parameters.MAX_TRACES -> Specify the maximum number of traces to import from the log (read in order in the XML file)
            Parameters.MAX_BYTES -> Maximum number of bytes to read
            Parameters.SKYP_BYTES -> Number of bytes to skip


    Returns
    -----------
    log
        Log file
    """
    if parameters is None:
        parameters = {}

    file_size = os.stat(filename).st_size

    f = open(filename, "r")
    log = import_log_from_file_object(f, file_size=file_size, parameters=parameters)
    f.close()

    return log


def import_from_string(log_string, parameters=None):
    """
    Deserialize a text/binary string representing a XES log

    Parameters
    -----------
    log_string
        String that contains the XES
    parameters
        Parameters of the algorithm, including
            Parameters.TIMESTAMP_SORT -> Specify if we should sort log by timestamp
            Parameters.TIMESTAMP_KEY -> If sort is enabled, then sort the log by using this key
            Parameters.REVERSE_SORT -> Specify in which direction the log should be sorted
            Parameters.INSERT_TRACE_INDICES -> Specify if trace indexes should be added as event attribute for each event
            Parameters.MAX_TRACES -> Specify the maximum number of traces to import from the log (read in order in the XML file)

    Returns
    -----------
    log
        Trace log object
    """
    if parameters is None:
        parameters = {}

    if type(log_string) is bytes:
        log_string = log_string.decode(constants.DEFAULT_ENCODING)

    return import_log_from_file_object(StringIO(log_string), parameters=parameters)
