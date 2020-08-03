from enum import Enum
from pm4py.util import xes_constants
from pm4py.util import constants
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.util import exec_utils
from pm4py.algo.discovery.causal import algorithm as causal_discovery
from pm4py.algo.discovery.footprints.outputs import Outputs


class Parameters(Enum):
    SORT_REQUIRED = "sort_required"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    INDEX_KEY = "index_key"


DEFAULT_SORT_REQUIRED = True
DEFAULT_INDEX_KEY = "@@index"


def apply(df, parameters=None):
    """
    Discovers a footprint object from a dataframe
    (the footprints of the dataframe are returned)

    Parameters
    --------------
    df
        Dataframe
    parameters
        Parameters of the algorithm

    Returns
    --------------
    footprints_obj
        Footprints object
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    caseid_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    sort_required = exec_utils.get_param_value(Parameters.SORT_REQUIRED, parameters, DEFAULT_SORT_REQUIRED)
    index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, DEFAULT_INDEX_KEY)

    df = df[[caseid_key, activity_key, timestamp_key]]
    if sort_required:
        df[index_key] = df.index
        df = df.sort_values([caseid_key, timestamp_key, index_key])

    grouped_df = df.groupby(caseid_key)
    dfg = df_statistics.get_dfg_graph(df, measure="frequency", activity_key=activity_key, case_id_glue=caseid_key,
                                      timestamp_key=timestamp_key, sort_caseid_required=False,
                                      sort_timestamp_along_case_id=False)
    activities = set(df[activity_key].unique())
    start_activities = set(grouped_df.first()[activity_key].unique())
    end_activities = set(grouped_df.last()[activity_key].unique())

    parallel = {(x, y) for (x, y) in dfg if (y, x) in dfg}
    sequence = set(causal_discovery.apply(dfg, causal_discovery.Variants.CAUSAL_ALPHA))

    ret = {}
    ret[Outputs.DFG.value] = dfg
    ret[Outputs.SEQUENCE.value] = sequence
    ret[Outputs.PARALLEL.value] = parallel
    ret[Outputs.ACTIVITIES.value] = activities
    ret[Outputs.START_ACTIVITIES.value] = start_activities
    ret[Outputs.END_ACTIVITIES.value] = end_activities
    ret[Outputs.MIN_TRACE_LENGTH.value] = int(grouped_df.size().min())

    return ret
