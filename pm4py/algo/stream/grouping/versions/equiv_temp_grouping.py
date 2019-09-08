EQUIV_COLUMNS = "equiv_columns"
TIME_DELAY = "time_delay"
TIMESTAMP_COLUMN = "timestamp_column"
DEFAULT_TIMEST_COLUMN = "current_timestamp"


def apply(stream, parameters=None):
    """
    Applies a grouping into sentences to a stream

    Parameters
    -------------
    stream
        Event stream
    parameters
        Parameters of the algorithm, including:
            equiv_columns => Columns that shall be equal in order for two successive events to belong to
                the same group
            time_Delay => The delay that is considered for grouping two successive events into the
                same group

    Returns
    -------------
    grouped_stream
        Grouped event stream
    """
    if parameters is None:
        parameters = {}

    equiv_columns = sorted(parameters[EQUIV_COLUMNS]) if EQUIV_COLUMNS in parameters else []
    time_delay = parameters[TIME_DELAY] if TIME_DELAY in parameters else 5
    timestamp_column = parameters[TIMESTAMP_COLUMN] if TIMESTAMP_COLUMN in parameters else DEFAULT_TIMEST_COLUMN

    grouped_stream = []

    for i in range(len(stream)):
        if i == 0:
            grouped_stream.append([stream[i]])
        else:
            e_col = sorted([col for col in stream[i].keys() if stream[i][col] == stream[i-1][col]])
            time_i = stream[i][timestamp_column]
            time_i1 = stream[i-1][timestamp_column]
            if e_col == equiv_columns or (time_i - time_i1) < time_delay:
                grouped_stream[-1].append(stream[i])
            else:
                grouped_stream.append([stream[i]])

    return grouped_stream
