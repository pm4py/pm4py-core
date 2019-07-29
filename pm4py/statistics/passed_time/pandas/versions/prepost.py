from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY, \
    PARAMETER_CONSTANT_TIMESTAMP_KEY
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY, DEFAULT_TIMESTAMP_KEY
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics


def apply(df, activity, parameters=None):
    """
    Gets the time passed from each preceding activity and to each succeeding activity

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
        Dictionary containing a 'pre' key with the
        list of aggregated times from each preceding activity to the given activity
        and a 'post' key with the list of aggregates times from the given activity
        to each succeeding activity
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY

    dfg = df_statistics.get_dfg_graph(df, measure="performance", activity_key=activity_key,
                                           case_id_glue=case_id_glue, timestamp_key=timestamp_key)

    pre = []
    post = []

    for entry in dfg.keys():
        if entry[1] == activity:
            pre.append([entry[0], float(dfg[entry])])
        if entry[0] == activity:
            post.append([entry[1], float(dfg[entry])])

    return {"pre": pre, "post": post}
