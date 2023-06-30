from pm4py.objects.petri_net.obj import PetriNet, Marking
from typing import Optional, Dict, Any
from pm4py.algo.querying.llm.abstractions import net_to_descr
from pm4py.algo.querying.llm.connectors import openai as perform_query
from enum import Enum
from pm4py.util import exec_utils, constants


class Parameters(Enum):
    EXECUTE_QUERY = "execute_query"
    API_KEY = "api_key"
    EXEC_RESULT = "exec_result"


AVAILABLE_QUERIES = ["petri_diff_with_de_jure", "petri_describe_process"]


def query_wrapper(net: PetriNet, im: Marking, fm: Marking, type: str, args: Optional[Dict[Any, Any]] = None, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    if args is None:
        args = {}

    if type == "petri_diff_with_de_jure":
        return petri_diff_with_de_jure(net, im, fm, parameters=parameters)
    elif type == "petri_describe_process":
        return petri_describe_process(net, im, fm, parameters=parameters)


def petri_diff_with_de_jure(net: PetriNet, im: Marking, fm: Marking, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = net_to_descr.apply(net, im, fm, parameters=parameters)
    query += "what are the differences of this process model with what would you expect (de-jure model) for the same process? Please only provide data or process-specific information, i.e., if the context is insufficient please not report any general consideration"

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)


def petri_describe_process(net: PetriNet, im: Marking, fm: Marking, parameters: Optional[Dict[Any, Any]] = None) -> str:
    if parameters is None:
        parameters = {}

    api_key = exec_utils.get_param_value(Parameters.API_KEY, parameters, constants.OPENAI_API_KEY)
    execute_query = exec_utils.get_param_value(Parameters.EXECUTE_QUERY, parameters, api_key is not None)

    query = net_to_descr.apply(net, im, fm, parameters=parameters)
    query += "could you describe the process represented in this Petri net?"

    if not execute_query:
        return query

    return perform_query.apply(query, parameters=parameters)
