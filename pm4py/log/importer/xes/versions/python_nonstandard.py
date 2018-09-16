from itertools import islice
from pm4py import log as log_lib
import ciso8601

def import_log(filename, parameters=None):
    """
    Import a TraceLog object from a XML file
    containing the traces, the events and the simple attributes of them

    Parameters
    -----------
    filename
        XES file to parse
    parameters
        Parameters of the algorithm

    Returns
    -----------
    xes
        XES file
    """
    if parameters is None:
        parameters = {}
    log = log_lib.log.TraceLog()
    trace = None
    event = None
    with open(filename, "r") as f:
        for line in f:
            content = line.split("\"")
            tag = content[0].split("<")[1]
            if not trace is None:
                if not event is None:
                    if len(content)==5:
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
                elif len(content)==5:
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
                    trace = None
            elif tag.startswith("trace"):
                trace = log_lib.log.Trace()
    return log