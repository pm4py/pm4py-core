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
from enum import Enum
from typing import Optional, Dict, Any

import pandas as pd

from pm4py.algo.discovery.dfg.adapters.pandas.df_statistics import get_partial_order_dataframe
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.util import typing


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    BUSINESS_HOURS = "business_hours"
    BUSINESS_HOUR_SLOTS = "business_hour_slots"
    WORKCALENDAR = "workcalendar"


def apply(df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> typing.TemporalProfile:
    """
    Gets the temporal profile from a dataframe.

    Implements the approach described in:
    Stertz, Florian, Jürgen Mangler, and Stefanie Rinderle-Ma. "Temporal Conformance Checking at Runtime based on Time-infused Process Models." arXiv preprint arXiv:2008.07262 (2020).


    Parameters
    ----------
    df
        Dataframe
    parameters
        Parameters, including:
        - Parameters.ACTIVITY_KEY => the column to use as activity
        - Parameters.START_TIMESTAMP_KEY => the column to use as start timestamp
        - Parameters.TIMESTAMP_KEY => the column to use as timestamp
        - Parameters.CASE_ID_KEY => the column to use as case ID

    Returns
    -------
    temporal_profile
        Temporal profile of the dataframe
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, None)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)

    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    business_hours_slots = exec_utils.get_param_value(Parameters.BUSINESS_HOUR_SLOTS, parameters, constants.DEFAULT_BUSINESS_HOUR_SLOTS)

    workcalendar = exec_utils.get_param_value(Parameters.WORKCALENDAR, parameters, constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR)

    efg = get_partial_order_dataframe(df, activity_key=activity_key, timestamp_key=timestamp_key,
                                      start_timestamp_key=start_timestamp_key, case_id_glue=case_id_key,
                                      keep_first_following=False, business_hours=business_hours, business_hours_slot=business_hours_slots, workcalendar=workcalendar)
    efg = efg[[activity_key, activity_key + "_2", "@@flow_time"]]
    temporal_profile = efg.groupby([activity_key, activity_key + "_2"]).agg(["mean", "std"]).reset_index().fillna(
        0).to_dict("records")

    temporal_profile = {
        (x[(activity_key, "")], x[(activity_key + "_2", "")]): (x[("@@flow_time", "mean")], x[("@@flow_time", "std")])
        for x in temporal_profile}

    return temporal_profile
