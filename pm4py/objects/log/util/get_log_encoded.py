import numpy as np


def get_log_encoded(event_log,
                    trace_attributes=[],
                    event_attributes=[],
                    concatenate=False):
    """
    Get event log encoded into matrix.

    Parameters
    ------------
    event_log
        Trace log
    trace_attributes
        Attributes of the trace to be encoded
    event_attributes
        Attributes of the events to be encoded
    concatenate
        Boolean indicating if to generate all sub-sequences of events in a trace

    Returns
    ------------
    dataset
        A numpy matrix with the event log
    columns
        The names of the columns in the dataset
    """
    columns = []
    dataset = []

    max_trace_len = 0

    for trace_index, trace in enumerate(event_log):
        trace_encoding = []
        tr_columns = []

        for trace_attribute in trace_attributes:
            tr_columns.append(trace_attribute)

            try:
                attr = trace.attributes[trace_attribute]
            except:
                attr = None
            trace_encoding.append(attr)

            for event_index, event in enumerate(trace):
                for event_attribute in event_attributes:
                    tr_columns.append(event_attribute)

                    try:
                        attr = event[event_attribute]
                    except:
                        attr = None
                    trace_encoding.append(attr)

                # For each trace in the event log, sequentially append the
                # event sequence until that event
                if concatenate is True:
                    if len(trace_encoding) > max_trace_len:
                        max_trace_len = len(trace_encoding)
                        columns = tr_columns

                    dataset.append(np.asarray(trace_encoding))

            if concatenate is not True:
                if len(trace_encoding) > max_trace_len:
                    max_trace_len = len(trace_encoding)
                    columns = tr_columns

                dataset.append(np.asarray(trace_encoding))

    dataset = np.asarray([np.pad(a,
                                 (0, max_trace_len - len(a)),
                                 'constant',
                                 constant_values=0) for a in dataset])

    columns = np.asarray(columns)

    return dataset, columns
