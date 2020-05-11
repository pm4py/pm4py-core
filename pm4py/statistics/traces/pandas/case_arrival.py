import pandas as pd

from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.statistics.parameters import Parameters
from pm4py.util import exec_utils


def get_case_arrival_avg(df, parameters=None):
    """
    Gets the average time interlapsed between case starts

    Parameters
    --------------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> attribute of the log to be used as timestamp

    Returns
    --------------
    case_arrival_avg
        Average time interlapsed between case starts
    """
    if parameters is None:
        parameters = {}

    caseid_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    timest_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    first_df = df.groupby(caseid_glue).first()

    first_df = first_df.sort_values(timest_key)

    first_df_shift = first_df.shift(-1)

    first_df_shift.columns = [str(col) + '_2' for col in first_df_shift.columns]

    df_successive_rows = pd.concat([first_df, first_df_shift], axis=1)
    df_successive_rows['interlapsed_time'] = (
            df_successive_rows[timest_key + '_2'] - df_successive_rows[timest_key]).astype('timedelta64[s]')

    df_successive_rows = df_successive_rows.dropna(subset=['interlapsed_time'])

    return df_successive_rows['interlapsed_time'].mean()
