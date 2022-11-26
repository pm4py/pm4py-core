from pm4py.algo.organizational_mining.roles.common import algorithm
from pm4py.util import xes_constants as xes
from collections import Counter
from pm4py.util import exec_utils

from enum import Enum
from pm4py.util import constants
from typing import Optional, Dict, Any, Union, List
import pandas as pd
from pm4py.objects.org.roles.obj import Role


class Parameters(Enum):
    ROLES_THRESHOLD_PARAMETER = "roles_threshold_parameter"
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(df: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> List[Role]:
    """
    Gets the roles (group of different activities done by similar resources)
    out of the log

    Parameters
    -------------
    df
        Pandas dataframe
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
    activity_resource_couples = Counter(dict(df.groupby([resource_key, activity_key]).size()))

    return algorithm.apply(activity_resource_couples, parameters=parameters)
