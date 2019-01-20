import pandas as pd

from pm4py.algo.enhancement.sna.transformer.common import df_utilities
from pm4py.objects.log.util import xes
from pm4py.objects.sna.matrix_container import MatrixContainer
from pm4py.util import constants


def apply(log, parameters=None):
    """
    Create basic matrix (containing only resources) from the trace log object

    Parameters
    ------------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            PARAMETER_CONSTANT_RESOURCE_KEY -> attribute key that contains the resource

    Returns
    ------------
    mco
        SNA Matrix container object
    """
    if parameters is None:
        parameters = {}

    resource_key = parameters[
        constants.PARAMETER_CONSTANT_RESOURCE_KEY] if constants.PARAMETER_CONSTANT_RESOURCE_KEY in parameters else xes.DEFAULT_RESOURCE_KEY
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    preliminary_list = []
    for case_index, case in enumerate(log):
        for event_index, event in enumerate(case):
            if (len(preliminary_list) > 0 and case_index == preliminary_list[len(preliminary_list) - 1]['trace_id']):
                try:
                    preliminary_list[len(preliminary_list) - 1]['next_resource'] = event[xes.DEFAULT_RESOURCE_KEY]
                except KeyError:
                    preliminary_list[len(preliminary_list) - 1]['next_resource'] = ":None:"
                # else:

            if (event_index == len(case) - 1):  # if it is the last event of the case, we will ignore it.
                continue  # because we need just the resource of it which is accessed by the previous statement

            sndict = {}
            try:
                sndict['resource'] = event["org:resource"]
            except KeyError:
                sndict['resource'] = ":None:"

            sndict['next_resource'] = ""
            sndict['relation_depth'] = "1"
            sndict['trace_length'] = len(case)
            sndict['trace_id'] = case_index
            preliminary_list.append(sndict)

    basic_df = pd.DataFrame(preliminary_list)
    resources_set = df_utilities.get_resources_from_df(basic_df)

    mco = MatrixContainer(basic_df, resources_set)

    return mco
