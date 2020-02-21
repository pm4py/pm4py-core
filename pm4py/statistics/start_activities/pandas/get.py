from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import GROUPED_DATAFRAME

def get_start_activities(df, parameters=None):
    """
    Get start activities count

    Parameters
    -----------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
            case_id_glue -> Case ID column in the dataframe
            activity_key -> Column that represents the activity

    Returns
    -----------
    startact_dict
        Dictionary of start activities along with their count
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    grouped_df = parameters[GROUPED_DATAFRAME] if GROUPED_DATAFRAME in parameters else df.groupby(case_id_glue)

    first_eve_df = grouped_df.first()
    startact_dict = dict(first_eve_df[activity_key].value_counts())
    return startact_dict