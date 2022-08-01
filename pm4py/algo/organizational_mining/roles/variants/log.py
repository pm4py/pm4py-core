from pm4py.algo.organizational_mining.roles.common import algorithm
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.util import xes_constants as xes
from collections import Counter
from pm4py.util import exec_utils
from enum import Enum
from pm4py.util import constants
from typing import Optional, Dict, Any, Union, List
from pm4py.objects.log.obj import EventLog
from pm4py.objects.org.roles.obj import Role


class Parameters(Enum):
    ROLES_THRESHOLD_PARAMETER = "roles_threshold_parameter"
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> List[Role]:
    """
    Gets the roles (group of different activities done by similar resources)
    out of the log

    Parameters
    -------------
    log
        Log object
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    roles
        List of different roles inside the log
    """
    if parameters is None:
        parameters = {}

    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes.DEFAULT_RESOURCE_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)

    stream = log_converter.apply(log, variant=log_converter.TO_EVENT_STREAM, parameters={"deepcopy": False, "include_case_attributes": False})

    activity_resource_couples = Counter((event[resource_key], event[activity_key]) for event in stream)

    return algorithm.apply(activity_resource_couples, parameters=parameters)
