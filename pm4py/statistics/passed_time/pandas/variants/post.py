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
from pm4py.statistics.parameters import Parameters
from pm4py.util.xes_constants import DEFAULT_NAME_KEY, DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.objects.dfg.retrieval import pandas
from pm4py.util import exec_utils


def apply(df, activity, parameters=None):
    """
    Gets the time passed to each succeeding activity

    Parameters
    -------------
    df
        Dataframe
    activity
        Activity that we are considering
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    dictio
        Dictionary containing a 'post' key with the
        list of aggregates times from the given activity to each succeeding activity
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, None)

    [dfg_frequency, dfg_performance] = pandas.get_dfg_graph(df, measure="both", activity_key=activity_key,
                                           case_id_glue=case_id_glue, timestamp_key=timestamp_key,
                                                            start_timestamp_key=start_timestamp_key)

    post = []
    sum_perf_post = 0.0
    sum_acti_post = 0.0

    for entry in dfg_performance.keys():
        if entry[0] == activity:
            post.append([entry[1], float(dfg_performance[entry]), int(dfg_frequency[entry])])
            sum_perf_post = sum_perf_post + float(dfg_performance[entry]) * float(dfg_frequency[entry])
            sum_acti_post = sum_acti_post + float(dfg_frequency[entry])

    perf_acti_post = 0.0
    if sum_acti_post > 0:
        perf_acti_post = sum_perf_post / sum_acti_post

    return {"post": post, "post_avg_perf": perf_acti_post}
