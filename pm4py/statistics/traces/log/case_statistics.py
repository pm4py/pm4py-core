from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.objects.log.util.xes import DEFAULT_TRACEID_KEY
from pm4py.statistics.traces.common import case_duration as case_duration_commons
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY


def get_variant_statistics(log, parameters=None):
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces that share the variant

    Parameters
    ----------
    log
        Log
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
    varnt = parameters["variants"] if "variants" in parameters else variants_filter.get_variants(log,
                                                                                                 parameters=parameters)
    variants_list = []
    for var in varnt:
        variants_list.append({"variant": var, "count": len(varnt[var])})
    variants_list = sorted(variants_list, key=lambda x: x["count"], reverse=True)
    if max_variants_to_return:
        variants_list = variants_list[:min(len(variants_list), max_variants_to_return)]
    return variants_list


def get_cases_description(log, parameters=None):
    """
    Get a description of traces present in the log

    Parameters
    -----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
        case_id_key -> Trace attribute in which the case ID is contained
        timestamp_key -> Column that identifies the timestamp
        enable_sort -> Enable sorting of traces
        sort_by_index ->         Sort the traces using this index:
            0 -> case ID
            1 -> start time
            2 -> end time
            3 -> difference
        sort_ascending -> Set sort direction (boolean; it true then the sort direction is ascending, otherwise
        descending)
        max_ret_cases -> Set the maximum number of returned traces

    Returns
    -----------
    ret
        Dictionary of traces associated to their start timestamp, their end timestamp and their duration
    """

    if parameters is None:
        parameters = {}

    case_id_key = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else DEFAULT_TRACEID_KEY
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    enable_sort = parameters["enable_sort"] if "enable_sort" in parameters else True
    sort_by_index = parameters["sort_by_index"] if "sort_by_index" in parameters else 0
    sort_ascending = parameters["sort_ascending"] if "sort_ascending" in parameters else True
    max_ret_cases = parameters["max_ret_cases"] if "max_ret_cases" in parameters else None

    statistics_list = []

    for trace in log:
        if trace:
            ci = trace.attributes[case_id_key]
            st = trace[0][timestamp_key].timestamp()
            et = trace[-1][timestamp_key].timestamp()
            diff = et - st
            statistics_list.append([ci, st, et, diff])

    if enable_sort:
        statistics_list = sorted(statistics_list, key=lambda x: x[sort_by_index], reverse=not sort_ascending)

    if max_ret_cases is not None:
        statistics_list = statistics_list[:min(len(statistics_list), max_ret_cases)]

    statistics_dict = {}

    for el in statistics_list:
        statistics_dict[str(el[0])] = {"startTime": el[1], "endTime": el[2], "caseDuration": el[3]}

    return statistics_dict


def index_log_caseid(log, parameters=None):
    """
    Index a log according to case ID

    Parameters
    -----------
    log
        Log object
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

    case_id_key = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else DEFAULT_TRACEID_KEY
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
        Log object
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
    indexed_log = parameters["indexed_log"] if "indexed_log" in parameters else index_log_caseid(log,
                                                                                                 parameters)
    list_eve = []
    for event in indexed_log[case_id]:
        list_eve.append(dict(event))
    return list_eve


def get_all_casedurations(log, parameters=None):
    """
    Gets all the case durations out of the log

    Parameters
    ------------
    log
        Log object
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    duration_values
        List of all duration values
    """
    cases = get_cases_description(log, parameters=parameters)
    duration_values = [x["caseDuration"] for x in cases.values()]

    return sorted(duration_values)


def get_first_quartile_caseduration(log, parameters=None):
    """
    Gets the first quartile out of the log

    Parameters
    -------------
    log
        Log
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    value
        First quartile value
    """
    duration_values = get_all_casedurations(log, parameters=parameters)
    if duration_values:
        return duration_values[int((len(duration_values) * 3) / 4)]
    return 0


def get_median_caseduration(log, parameters=None):
    """
    Gets the median case duration out of the log

    Parameters
    -------------
    log
        Log
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    value
        Median duration value
    """
    duration_values = get_all_casedurations(log, parameters=parameters)
    if duration_values:
        return duration_values[int(len(duration_values) / 2)]
    return 0


def get_kde_caseduration(log, parameters=None):
    """
    Gets the estimation of KDE density for the case durations calculated on the log

    Parameters
    --------------
    log
        Log object
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph

    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    return case_duration_commons.get_kde_caseduration(get_all_casedurations(log, parameters=parameters),
                                                      parameters=parameters)


def get_kde_caseduration_json(log, parameters=None):
    """
    Gets the estimation of KDE density for the case durations calculated on the log
    (expressed as JSON)

    Parameters
    --------------
    log
        Log object
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph
            case_id_glue -> Column hosting the Case ID

    Returns
    --------------
    json
        JSON representing the graph points
    """
    cases = get_cases_description(log, parameters=parameters)
    duration_values = [x["caseDuration"] for x in cases.values()]

    return case_duration_commons.get_kde_caseduration_json(duration_values, parameters=parameters)
