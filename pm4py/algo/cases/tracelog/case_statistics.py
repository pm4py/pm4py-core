from pm4py.util import constants
from pm4py.entities.log.util import xes
from pm4py.algo.filtering.tracelog.variants import variants_filter

def get_variant_statistics(trace_log, parameters=None):
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces that share the variant

    Parameters
    ----------
    trace_log
        Trace log
    parameters
        Parameters of the algorithm, including:
            activity_key -> Attribute identifying the activity in the log
            max_variants_to_return -> Maximum number of variants to return
            variants -> If provided, avoid recalculation of the variants

    Returns
    ----------
    variants_list
        List of variants along the statistics
    """

    if parameters is None:
        parameters = {}
    max_variants_to_return = parameters["max_variants_to_return"] if "max_variants_to_return" in parameters else None
    variants = parameters["variants"] if "variants" in parameters else variants_filter.get_variants(trace_log, parameters=parameters)
    variants_list = []
    for variant in variants:
        variants_list.append({"variant": variant, "count": len(variants[variant])})
    if max_variants_to_return:
        variants_list = variants_list[:min(len(variants_list), max_variants_to_return)]
    return variants_list

def get_cases_description(trace_log, parameters=None):
    """
    Get a description of cases present in the trace log

    Parameters
    -----------
    trace_log
        Trace log
    parameters
        Parameters of the algorithm, including:
        case_id_key -> Trace attribute in which the case ID is contained
        timestamp_key -> Column that identifies the timestamp
        enable_sort -> Enable sorting of cases
        sort_by_index ->         Sort the cases using this index:
            0 -> case ID
            1 -> start time
            2 -> end time
            3 -> difference
        sort_ascending -> Set sort direction (boolean; it true then the sort direction is ascending, otherwise descending)
        max_ret_cases -> Set the maximum number of returned cases

    Returns
    -----------
    ret
        Dictionary of cases associated to their start timestamp, their end timestamp and their duration
    """

    if parameters is None:
        parameters = {}

    case_id_key = parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else xes.DEFAULT_TRACEID_KEY
    timestamp_key = parameters[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    enable_sort = parameters["enable_sort"] if "enable_sort" in parameters else True
    sort_by_index = parameters["sort_by_index"] if "sort_by_index" in parameters else 0
    sort_ascending = parameters["sort_ascending"] if "sort_ascending" in parameters else "ascending"
    max_ret_cases = parameters["max_ret_cases"] if "max_ret_cases" in parameters else None

    statistics_list = []

    for trace in trace_log:
        if trace:
            ci = trace.attributes[case_id_key]
            st = trace[0][timestamp_key].timestamp()
            et = trace[-1][timestamp_key].timestamp()
            diff = et - st
            statistics_list.append([ci, st, et, diff])

    if enable_sort:
        statistics_list = sorted(statistics_list, key=lambda x: x[sort_by_index], reverse=not(sort_ascending))

    if max_ret_cases is not None:
        statistics_list = statistics_list[:max(len(statistics_list), max_ret_cases)]

    statistics_dict = {}

    for el in statistics_list:
        statistics_dict[str(el[0])] = {"startTime": el[1], "endTime": el[2], "caseDuration": el[3]}

    return statistics_dict

def index_tracelog_accordingto_caseid(log, case_id, parameters=None):
    """
    Index a trace log according to case ID

    Parameters
    -----------
    log
        Trace log object
    case_id
        Required case ID
    parameters
        Possible parameters of the algorithm, including:
            case id key -> Trace attribute in which the Case ID is contained

    Returns
    -----------
    dict
        Dictionary that has the case IDs as keys and the corresponding case as value
    """

    if parameters is None:
        parameters = {}

    case_id_key = parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else xes.DEFAULT_TRACEID_KEY
    indexed_log = {}

    for trace in log:
        trace_id = trace.attributes[case_id_key]
        indexed_log[trace_id] = trace

    return indexed_log

def get_events(log, case_id, parameters=None):
    """
    Get events belonging to the specified case

    Parameters
    -----------
    log
        Trace log object
    case_id
        Required case ID
    parameters
        Possible parameters of the algorithm, including:
            case id key -> Trace attribute in which the case ID is contained
            indexed_log -> Indexed log (if it has been calculated previously)

    Returns
    ----------
    list_eve
        List of events belonging to the case
    """
    if parameters is None:
        parameters = {}
    indexed_log = parameters["indexed_log"] if "indexed_log" in parameters else index_tracelog_accordingto_caseid(log, parameters)
    list_eve = []
    for event in indexed_log[case_id]:
        list_eve.append(dict(event))
    return list_eve