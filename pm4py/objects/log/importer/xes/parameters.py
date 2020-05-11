from enum import Enum

class Parameters(Enum):
    TIMESTAMP_SORT = 'timestamp_sort'
    TIMESTAMP_KEY = 'timestamp_key'
    REVERSE_SORT = 'reverse_sort'
    INSERT_TRACE_INDICES = 'insert_trace_indexes'
    MAX_TRACES = 'max_no_traces_to_import'
