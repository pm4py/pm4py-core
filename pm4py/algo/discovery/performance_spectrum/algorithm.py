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
from pm4py.algo.discovery.performance_spectrum.variants import dataframe, log, dataframe_disconnected, log_disconnected
from pm4py.util import exec_utils
from enum import Enum
from pm4py.util import constants, pandas_utils
from typing import Optional, Dict, Any, Union, List
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    PARAMETER_SAMPLE_SIZE = "sample_size"


class Outputs(Enum):
    LIST_ACTIVITIES = "list_activities"
    POINTS = "points"


class Variants(Enum):
    DATAFRAME = dataframe
    LOG = log
    DATAFRAME_DISCONNECTED = dataframe_disconnected
    LOG_DISCONNECTED = log_disconnected


def apply(log: Union[EventLog, EventStream, pd.DataFrame], list_activities: List[str], variant=None, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Finds the performance spectrum provided a log/dataframe
    and a list of activities

    Parameters
    -------------
    log
        Event log/Dataframe
    list_activities
        List of activities interesting for the performance spectrum (at least two)
    variant
        Variant to be used (see Variants Enum)
    parameters
        Parameters of the algorithm, including:
            - Parameters.ACTIVITY_KEY
            - Parameters.TIMESTAMP_KEY

    Returns
    -------------
    ps
        Performance spectrum object (dictionary)
    """
    from pm4py.objects.conversion.log import converter as log_conversion

    if parameters is None:
        parameters = {}

    sample_size = exec_utils.get_param_value(Parameters.PARAMETER_SAMPLE_SIZE, parameters, 10000)

    if len(list_activities) < 2:
        raise Exception("performance spectrum can be applied providing at least two activities!")

    points = None

    if pandas_utils.check_is_pandas_dataframe(log):
        if variant is None:
            variant = Variants.DATAFRAME

        points = exec_utils.get_variant(variant).apply(log, list_activities, sample_size, parameters)

    if points is None:
        if variant is None:
            variant = Variants.LOG

        points = exec_utils.get_variant(variant).apply(log_conversion.apply(log, variant=log_conversion.Variants.TO_EVENT_LOG, parameters=parameters), list_activities, sample_size,
                                                            parameters)

    ps = {Outputs.LIST_ACTIVITIES.value: list_activities, Outputs.POINTS.value: points}

    return ps
