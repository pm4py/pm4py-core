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
from pm4py.algo.discovery.dfg.variants import native, performance
from typing import Optional, Dict, Any
from pm4py.objects.log.obj import EventLog
from pm4py.objects.conversion.log import converter as log_converter


def apply(log: EventLog, activity: str, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Gets the time passed to each succeeding activity

    Parameters
    -------------
    log
        Log
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

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    dfg_frequency = native.native(log, parameters=parameters)
    dfg_performance = performance.performance(log, parameters=parameters)

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
