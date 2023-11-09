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
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.statistics.start_activities.pandas.get import get_start_activities
from pm4py.util import xes_constants as xes
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import GROUPED_DATAFRAME
from enum import Enum
from pm4py.util import exec_utils
from copy import copy
from typing import Optional, Dict, Any, Union, List
import pandas as pd


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    DECREASING_FACTOR = "decreasingFactor"
    GROUP_DATAFRAME = GROUPED_DATAFRAME
    POSITIVE = "positive"


def apply(df: pd.DataFrame, values: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Filter dataframe on start activities

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the dataframe
            Parameters.ACTIVITY_KEY -> Column that represents the activity
            Parameters.POSITIVE -> Specifies if the filtered should be applied including traces (positive=True)
            or excluding traces (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    grouped_df = exec_utils.get_param_value(Parameters.GROUP_DATAFRAME, parameters, None)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    return filter_df_on_start_activities(df, values, case_id_glue=case_id_glue, activity_key=activity_key,
                                         positive=positive, grouped_df=grouped_df)


def filter_df_on_start_activities(df, values, case_id_glue=CASE_CONCEPT_NAME,
                                  activity_key=xes.DEFAULT_NAME_KEY, grouped_df=None, positive=True):
    """
    Filter dataframe on start activities

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    case_id_glue
        Case ID column in the dataframe
    activity_key
        Column that represent the activity
    grouped_df
        Grouped dataframe
    positive
        Specifies if the filtered should be applied including traces (positive=True) or excluding traces
        (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """

    if grouped_df is None:
        grouped_df = df.groupby(case_id_glue, sort=False)
    gdf = grouped_df[activity_key].first().isin(values)
    i1 = df.set_index(case_id_glue).index
    i2 = gdf[gdf].index
    if positive:
        ret = df[i1.isin(i2)]
    else:
        ret = df[~i1.isin(i2)]

    ret.attrs = copy(df.attrs) if hasattr(df, 'attrs') else {}
    return ret


def filter_df_on_start_activities_nocc(df, nocc, sa_count0=None, case_id_glue=CASE_CONCEPT_NAME,
                                       activity_key=DEFAULT_NAME_KEY, grouped_df=None):
    """
    Filter dataframe on start activities number of occurrences

    Parameters
    -----------
    df
        Dataframe
    nocc
        Minimum number of occurrences of the start activity
    sa_count0
        (if provided) Dictionary that associates each start activity with its count
    case_id_glue
        Column that contains the Case ID
    activity_key
        Column that contains the activity
    grouped_df
        Grouped dataframe

    Returns
    ------------
    df
        Filtered dataframe
    """
    if grouped_df is None:
        grouped_df = df.groupby(case_id_glue, sort=False)
    first_eve_df = grouped_df.first()
    if sa_count0 is None:
        parameters = {
            Parameters.CASE_ID_KEY: case_id_glue,
            Parameters.ACTIVITY_KEY: activity_key,
            Parameters.GROUP_DATAFRAME: grouped_df
        }
        sa_count0 = get_start_activities(df, parameters=parameters)
    sa_count = [k for k, v in sa_count0.items() if v >= nocc]
    if len(sa_count) < len(sa_count0):
        first_eve_df = first_eve_df[first_eve_df[activity_key].isin(sa_count)]
        i1 = df.set_index(case_id_glue).index
        i2 = first_eve_df.index
        ret = df[i1.isin(i2)]
    else:
        ret = df

    ret.attrs = copy(df.attrs) if hasattr(df, 'attrs') else {}
    return ret
