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
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Optional, Dict, Any, Union
from pm4py.util import constants, xes_constants, exec_utils
from pm4py.objects.conversion.log import converter as log_converter
from enum import Enum


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    FILTER_TYPE = "filter_type"


def apply(log_obj: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Groups the events of the same case happening at the same timestamp,
    providing option to keep the first event of each group, keep the last event of each group, create an event
    having as activity the concatenation of the activities happening in the group

    Parameters
    ---------------
    log_obj
        Log object (EventLog, EventStream, Pandas dataframe)
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY => the case identifier to be used
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity
        - Parameters.TIMESTAMP_KEY => the attribute to be used as timestamp
        - Parameters.FILTER_TYPE => the type of filter to be applied:
            first => keeps the first event of each group
            last => keeps the last event of each group
            concat => creates an event having as activity the concatenation of the activities happening in the group

    Returns
    ---------------
    filtered_dataframe
        Filtered dataframe object
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    filter_type = exec_utils.get_param_value(Parameters.FILTER_TYPE, parameters, "first")

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    gdf = log_obj.groupby([case_id_key, timestamp_key], sort=False)

    ret = None
    if filter_type == "first":
        ret = gdf.first()
    elif filter_type == "last":
        ret = gdf.last()
    elif filter_type == "concat":
        ret = gdf.first()
        ret[activity_key] = gdf[activity_key].agg(list).apply(lambda x: " & ".join(sorted(list(x))))

    ret = ret.reset_index()
    return ret
