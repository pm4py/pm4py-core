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