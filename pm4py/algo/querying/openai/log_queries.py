from typing import Optional, Dict, Any, Collection
import pandas as pd
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.ocel.obj import OCEL
from pm4py.algo.querying.openai import log_to_dfg_descr, log_to_variants_descr, log_to_cols_descr
from pm4py.algo.querying.openai import stream_to_descr
from pm4py.algo.transformation.ocel.description import algorithm as ocel_description
from pm4py.algo.querying.openai import ocel_ocdfg_descr
from pm4py.algo.querying.openai import perform_query
from pm4py.objects.conversion.log import converter as log_converter
from typing import Union, Tuple
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants


class Parameters(Enum):
    EXECUTE_QUERY = "execute_query"
    API_KEY = "api_key"
    EXEC_RESULT = "exec_result"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


AVAILABLE_LOG_QUERIES = ["describe_process", "describe_path", "describe_activity", "suggest_improvements", "code_for_log_generation",
                         "root_cause_analysis", "describe_variant", "compare_logs", "anomaly_detection", "suggest_clusters",
                         "conformance_checking", "suggest_verify_hypotheses", "filtering_query",
                         "abstract_dfg", "abstract_variants", "abstract_columns", "abstract_ocel", "abstract_stream", "abstract_ocel_ocdfg"]


def query_wrapper(log_obj: Union[pd.DataFrame, EventLog, EventStream, OCEL], type: str, args: Optional[Dict[Any, Any]] = None, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    if args is None:
        args = {}

    if type == "describe_process":
        return describe_process(log_obj, parameters=parameters)
    elif type == "describe_path":
        return describe_path(log_obj, (args["source"], args["target"]), parameters=parameters)
    elif type == "describe_activity":
        return describe_activity(log_obj, args["activity"], parameters=parameters)
    elif type == "suggest_improvements":
        return suggest_improvements(log_obj, parameters=parameters)
    elif type == "anomalous_paths":
        return anomalous_paths(log_obj, parameters=parameters)
    elif type == "code_for_log_generation":
        return code_for_log_generation(args["desired_process"], parameters=parameters)
    elif type == "root_cause_analysis":
        return root_cause_analysis(log_obj, parameters=parameters)
    elif type == "describe_variant":
        return describe_variant(log_obj, args["variant"], parameters=parameters)
    elif type == "compare_logs":
        return compare_logs(log_obj, args["log2"], parameters=parameters)
    elif type == "anomaly_detection":
        return anomaly_detection(log_obj, parameters=parameters)
    elif type == "suggest_clusters":
        return suggest_clusters(log_obj, parameters=parameters)
    elif type == "conformance_checking":
        return conformance_checking(log_obj, args["rule"], parameters=parameters)
    elif type == "suggest_verify_hypotheses":
        return suggest_verify_hypotheses(log_obj, parameters=parameters)
    elif type == "filtering_query":
        return filtering_query(log_obj, args["query"], parameters=parameters)
    elif type == "abstract_dfg":
        return log_to_dfg_descr.apply(log_obj, parameters=parameters)
    elif type == "abstract_variants":
        return log_to_variants_descr.apply(log_obj, parameters=parameters)
    elif type == "abstract_columns":
        return log_to_cols_descr.apply(log_obj, parameters=parameters)
    elif type == "abstract_ocel":
        return ocel_description.apply(log_obj, parameters=parameters)
    elif type == "abstract_stream":
        return stream_to_descr.apply(log_obj, parameters=parameters)
    elif type == "abstract_ocel_ocdfg":
        return ocel_ocdfg_descr.apply(log_obj, parameters=parameters)


def describe_process(log_obj: Union[pd.DataFrame, EventLog, EventStream], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = log_to_dfg_descr.apply(log_obj, parameters=parameters)
    query += "can you provide a description of the process?"

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def describe_path(log_obj: Union[pd.DataFrame, EventLog, EventStream], path: Tuple[str, str], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = log_to_dfg_descr.apply(log_obj, parameters=parameters)
    query += "can you describe the meaning of the step "+path[0]+" -> "+path[1]+" ?"

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def describe_activity(log_obj: Union[pd.DataFrame, EventLog, EventStream], activity: str, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = log_to_dfg_descr.apply(log_obj, parameters=parameters)
    query += "can you describe the meaning of the activity "+activity+" ?"

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def suggest_improvements(log_obj: Union[pd.DataFrame, EventLog, EventStream], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = log_to_dfg_descr.apply(log_obj, parameters=parameters)
    query += "how to optimize the execution of the aforementioned process ?  Please only data and process specific considerations, not general considerations. Also, if possible, tell me which steps can be parallelized to increase the performance of the process."

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def anomalous_paths(log_obj: Union[pd.DataFrame, EventLog, EventStream], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = log_to_dfg_descr.apply(log_obj, parameters=parameters)
    query += "which are the paths, included in the directly-follows graph, that looks more anomalous? Could you also explain why they are anomalous? Please only data and process specific considerations, not general considerations."

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def code_for_log_generation(desired_process: str, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)
    exec_result = exec_utils.get_param_value(Parameters.EXEC_RESULT, parameters, constants.OPENAI_EXEC_RESULT)

    query = """Can you provide me some code to simulate a process? the result should be a Pandas dataframe where each row is an event containing the case/process execution (column case:concept:name), the activity (column concept:name) and timestamp (column time:timestamp).
several activities should be included in the dataframe, and the dataframe should contain some variations of the order of the activities. Additional columns related to the process can be included in the dataframe. The process to simulate is: """+desired_process+". Please provide me only the code."

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def root_cause_analysis(log_obj: Union[pd.DataFrame, EventLog, EventStream], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = log_to_variants_descr.apply(log_obj, parameters=parameters)
    query += "what are the root causes of the performance issues, given the considered process? Please only data and process specific considerations, not general considerations."

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def describe_variant(log_obj: Union[pd.DataFrame, EventLog, EventStream], variant: Collection[str], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = log_to_variants_descr.apply(log_obj, parameters=parameters)
    query += "can you describe (example, if you see something anomalous) the variant: "+" -> ".join(list(variant))

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def compare_logs(log1: Union[pd.DataFrame, EventLog, EventStream], log2: Union[pd.DataFrame, EventLog, EventStream], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log1 = log_converter.apply(log1, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    log2 = log_converter.apply(log2, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    log1_descr = log_to_dfg_descr.apply(log1, parameters={"relative_frequency": True, "response_header": False})
    log2_descr = log_to_dfg_descr.apply(log2, parameters={"relative_frequency": True, "response_header": False})

    query = "I want to compare the event log of a process containing the following steps (the frequency is relative to the number of cases):"
    query += log1_descr
    query += "with the event log of a process containing the following steps (the frequency is relative to the number of cases):"
    query += log2_descr
    query += "what are the main differences?"

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def anomaly_detection(log_obj: Union[pd.DataFrame, EventLog, EventStream], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)
    exec_result = exec_utils.get_param_value(Parameters.EXEC_RESULT, parameters, constants.OPENAI_EXEC_RESULT)

    query = log_to_variants_descr.apply(log_obj, parameters=parameters)
    query += "what are the main anomalies? An anomaly involves a strange ordering of the activities, or a significant amount of rework. Please only data and process specific considerations, not general considerations. Please sort the anomalies based on their seriousness."

    if not execute_query:
        return query

    res = perform_query.apply(query, parameters=parameters)

    return res


def suggest_clusters(log_obj: Union[pd.DataFrame, EventLog, EventStream], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)
    exec_result = exec_utils.get_param_value(Parameters.EXEC_RESULT, parameters, constants.OPENAI_EXEC_RESULT)

    query = log_to_variants_descr.apply(log_obj, parameters=parameters)
    query += "can you suggest some groups of variants (clusters) with intrinsic different behavior?"

    if not execute_query:
        return query

    res = perform_query.apply(query, parameters=parameters)

    return res


def conformance_checking(log_obj: Union[pd.DataFrame, EventLog, EventStream], rule: str, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)
    exec_result = exec_utils.get_param_value(Parameters.EXEC_RESULT, parameters, constants.OPENAI_EXEC_RESULT)

    query = log_to_variants_descr.apply(log_obj, parameters=parameters)
    query += "given the following conformance rule:\n"
    query += rule
    query += "\nwhat is the fitness level of the variants? can you identify some variants that violate such rule?"

    if not execute_query:
        return query

    res = perform_query.apply(query, parameters=parameters)

    return res


def suggest_verify_hypotheses(log_obj: Union[pd.DataFrame, EventLog, EventStream], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)
    exec_result = exec_utils.get_param_value(Parameters.EXEC_RESULT, parameters, constants.OPENAI_EXEC_RESULT)

    query = log_to_variants_descr.apply(log_obj, parameters=parameters)
    query += "\n\nand the log of the process contains the following attributes:\n\n"
    query += log_to_cols_descr.apply(log_obj, parameters=parameters)
    query += '\n\ncan you make some hyphothesis between the execution of the process and its attributes? I mean, can you provide me a DuckDB SQL query that I can execute, and return the results to you, in order for you to evaluate such hyphothesis about the process? More in detail, the data is stored in a Pandas dataframe where each row is an event having the provided attributes (so there are no separate table containing the variant). Can you tell me in advance which hyphothesis you want to verify? Please consider the following information: the case identifier is called "case:concept:name", the activity is stored inside the attribute "concept:name", the timestamp is stored inside the attribute "time:timestamp", the resource is stored inside the attribute "org:resource", there is not a variant column but that can be obtained as concatenation of the activities of a case, there is not a duration column but that can be obtained as difference between the timestamp of the first and the last event. Also, the dataframe is called "dataframe". You should use the EPOCH function of DuckDB to get the timestamp from the date.'

    if not execute_query:
        return query

    res = perform_query.apply(query, parameters=parameters)

    return res


def filtering_query(log_obj: Union[pd.DataFrame, EventLog, EventStream], filtering_query: str, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)
    exec_result = exec_utils.get_param_value(Parameters.EXEC_RESULT, parameters, constants.OPENAI_EXEC_RESULT)

    query = log_to_variants_descr.apply(log_obj, parameters=parameters)
    query += "\n\nand the log of the process contains the following attributes:\n\n"
    query += log_to_cols_descr.apply(log_obj, parameters=parameters)
    query += '\n\n'
    query += 'can you give me a DuckDB query giving me all the events of the cases for which there is at least an event satisfying the following query:\n'
    query += filtering_query
    query += '\n\nThe data is stored in a Pandas dataframe where each row is an event having the provided attributes (so there are no separate table containing the variant). Please consider the following information: the case identifier is called "case:concept:name", the activity is stored inside the attribute "concept:name", the timestamp is stored inside the attribute "time:timestamp", the resource is stored inside the attribute "org:resource", there is not a variant column but that can be obtained as concatenation of the activities of a case, there is not a duration column but that can be obtained as difference between the timestamp of the first and the last event. Also, the dataframe is called "dataframe". You should use the EPOCH function of DuckDB to get the timestamp from the date.'

    if not execute_query:
        return query

    res = perform_query.apply(query, parameters=parameters)

    return res
