from pm4py.objects.log.log import EventStream

RESOURCE_GROUP_COLUMN = "resource_group_column"
EQUIV_COLUMNS = "equiv_columns"
TIME_DELAY = "time_delay"
TIMESTAMP_COLUMN = "timestamp_column"
DEFAULT_RES_GROUP_COLUMN = "username"
DEFAULT_EQUIV_COLUMNS = ["process_name", "window_name"]
DEFAULT_TIMEST_COLUMN = "current_timestamp"


def apply(stream0, parameters=None):
    """
    Applies a grouping into sentences to a stream

    Parameters
    -------------
    stream0
        Event stream
    parameters
        Parameters of the algorithm, including:
            resource_group_column => The column that is associated to the resource, and is used to firstly
                group the stream
            equiv_columns => List of columns that shall be equal in order for two successive events to belong to
                the same group
            time_delay => The delay that is considered for grouping two successive events into the
                same group

    Returns
    -------------
    grouped_stream
        Grouped event stream
    """
    if parameters is None:
        parameters = {}

    res_group_column = parameters[
        RESOURCE_GROUP_COLUMN] if RESOURCE_GROUP_COLUMN in parameters else DEFAULT_RES_GROUP_COLUMN
    equiv_columns = set(parameters[EQUIV_COLUMNS]) if EQUIV_COLUMNS in parameters else set(DEFAULT_EQUIV_COLUMNS)
    time_delay = parameters[TIME_DELAY] if TIME_DELAY in parameters else 5
    timestamp_column = parameters[TIMESTAMP_COLUMN] if TIMESTAMP_COLUMN in parameters else DEFAULT_TIMEST_COLUMN

    resources = set(ev[res_group_column] for ev in stream0)

    grouped_stream = []

    for res in resources:
        stream = [x for x in stream0 if x[res_group_column] == res]
        for i in range(len(stream)):
            if i == 0:
                grouped_stream.append([stream[i]])
            else:
                e_col = set([col for col in stream[i].keys() if stream[i][col] == stream[i - 1][col]])
                time_i = stream[i][timestamp_column]
                time_i1 = stream[i - 1][timestamp_column]
                if e_col == equiv_columns or (time_i - time_i1) < time_delay:
                    grouped_stream[-1].append(stream[i])
                else:
                    grouped_stream.append([stream[i]])

    return EventStream(grouped_stream)
