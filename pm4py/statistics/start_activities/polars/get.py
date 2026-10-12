'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util import exec_utils
from pm4py.util import constants
from enum import Enum
from typing import Optional, Dict, Any, Union
import polars as pl


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    MAX_NO_POINTS_SAMPLE = "max_no_of_points_to_sample"
    KEEP_ONCE_PER_CASE = "keep_once_per_case"


def get_start_activities(
    lf: pl.LazyFrame,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Dict[str, int]:
    """
    Get start activities count

    Parameters
    -----------
    lf
        Polars LazyFrame
    parameters
        Parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the dataframe
            Parameters.ACTIVITY_KEY -> Column that represents the activity

    Returns
    -----------
    startact_dict
        Dictionary of start activities along with their count
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY
    )

    # Get the first activity for each case
    start_activities_df = (
        lf.group_by(case_id_glue)
        .agg(pl.col(activity_key).first().alias("start_activity"))
        .select("start_activity")
        .group_by("start_activity")
        .len(name="count")
        .collect()
    )

    # Convert to dictionary
    startact_dict = dict(
        zip(
            start_activities_df["start_activity"].to_list(),
            start_activities_df["count"].to_list()
        )
    )

    return startact_dict