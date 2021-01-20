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
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import GROUPED_DATAFRAME
from pm4py.statistics.parameters import Parameters
from pm4py.util import exec_utils


def get_start_activities(df, parameters=None):
    """
    Get start activities count

    Parameters
    -----------
    df
        Pandas dataframe
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

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    grouped_df = parameters[GROUPED_DATAFRAME] if GROUPED_DATAFRAME in parameters else df.groupby(case_id_glue)

    first_eve_df = grouped_df.first()
    startact_dict = dict(first_eve_df[activity_key].value_counts())
    return startact_dict