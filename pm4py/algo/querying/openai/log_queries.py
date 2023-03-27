'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''

from typing import Optional, Dict, Any, Collection
import pandas as pd
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.algo.querying.openai import log_to_dfg_descr, log_to_variants_descr
from pm4py.algo.querying.openai import perform_query
from typing import Union, Tuple
from enum import Enum
from pm4py.util import exec_utils, constants


class Parameters(Enum):
    EXECUTE_QUERY = "execute_query"
    API_KEY = "api_key"


AVAILABLE_LOG_QUERIES = ["describe_process", "describe_path", "describe_activity", "suggest_improvements", "code_for_log_generation",
                         "root_cause_analysis", "describe_variant", "compare_logs", "anomaly_detection", "suggest_clusters",
                         "conformance_checking"]


def query_wrapper(log_obj: Union[pd.DataFrame, EventLog, EventStream], type: str, args: Optional[Dict[Any, Any]] = None, parameters: Optional[Dict[Any, Any]] = None) -> str:
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


def describe_process(log_obj: Union[pd.DataFrame, EventLog, EventStream], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

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

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = log_to_dfg_descr.apply(log_obj, parameters=parameters)
    query += "how to optimize the execution of the aforementioned process ?  Please only data and process specific considerations, not general considerations. Also, if possible, tell me which steps can be parallelized to increase the performance of the process."

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def code_for_log_generation(desired_process: str, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = """Can you provide me some code to simulate a process? the result should be a Pandas dataframe where each row is an event containing the case/process execution (column case:concept:name), the activity (column concept:name) and timestamp (column time:timestamp).
several activities should be included in the dataframe, and the dataframe should contain some variations of the order of the activities. Additional columns related to the process can be included in the dataframe. The process to simulate is: """+desired_process+". Please provide me only the code."

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def root_cause_analysis(log_obj: Union[pd.DataFrame, EventLog, EventStream], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

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

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    log1_descr = log_to_dfg_descr.apply(log1, parameters={"relative_frequency": True, "response_header": False})
    log2_descr = log_to_dfg_descr.apply(log2, parameters={"relative_frequency": True, "response_header": False})

    query = "I want to compare the event log of a process containing the following steps (the frequency is relative to the number of cases):"
    query += log1_descr
    query += "ith the event log of a process containing the following steps (the frequency is relative to the number of cases):"
    query += log2_descr
    query += "what are the main differences?"

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def anomaly_detection(log_obj: Union[pd.DataFrame, EventLog, EventStream], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = log_to_variants_descr.apply(log_obj, parameters=parameters)
    query += "what are the main anomalies? An anomaly involves a strange ordering of the activities, or a significant amount of rework. Please only data and process specific considerations, not general considerations. Please sort the anomalies based on their seriousness."

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def suggest_clusters(log_obj: Union[pd.DataFrame, EventLog, EventStream], parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = log_to_variants_descr.apply(log_obj, parameters=parameters)
    query += "can you suggest some groups of variants (clusters) with intrinsic different behavior?"

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def conformance_checking(log_obj: Union[pd.DataFrame, EventLog, EventStream], rule: str, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = log_to_variants_descr.apply(log_obj, parameters=parameters)
    query += "given the following conformance rule:\n"
    query += rule
    query += "\nwhat is the fitness level of the variants? can you identify some variants that violate such rule?"

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)
