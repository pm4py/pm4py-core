import pandas as pd

from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY


def get_case_arrival_avg(df, parameters=None):
    """
    Gets the average time interlapsed between case starts

    Parameters
    --------------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
            PARAMETER_CONSTANT_TIMESTAMP_KEY -> attribute of the log to be used as timestamp

    Returns
    --------------
    case_arrival_avg
        Average time interlapsed between case starts
    """
    if parameters is None:
        parameters = {}

    if PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[PARAMETER_CONSTANT_CASEID_KEY] = CASE_CONCEPT_NAME
    if PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[PARAMETER_CONSTANT_ACTIVITY_KEY] = DEFAULT_NAME_KEY
    if PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[PARAMETER_CONSTANT_TIMESTAMP_KEY] = DEFAULT_TIMESTAMP_KEY
    if PARAMETER_CONSTANT_ATTRIBUTE_KEY not in parameters:
        parameters[PARAMETER_CONSTANT_ATTRIBUTE_KEY] = parameters[PARAMETER_CONSTANT_ACTIVITY_KEY]

    caseid_glue = parameters[PARAMETER_CONSTANT_CASEID_KEY]
    timest_key = parameters[PARAMETER_CONSTANT_TIMESTAMP_KEY]

    first_df = df.groupby(caseid_glue).first()

    first_df = first_df.sort_values(timest_key)

    first_df_shift = first_df.shift(-1)

    first_df_shift.columns = [str(col) + '_2' for col in first_df_shift.columns]

    df_successive_rows = pd.concat([first_df, first_df_shift], axis=1)
    df_successive_rows['interlapsed_time'] = (
            df_successive_rows[timest_key + '_2'] - df_successive_rows[timest_key]).astype('timedelta64[s]')

    df_successive_rows = df_successive_rows.dropna(subset=['interlapsed_time'])

    return df_successive_rows['interlapsed_time'].mean()
