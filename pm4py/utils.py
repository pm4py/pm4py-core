from pm4py.util import constants, xes_constants, pandas_utils

INDEX_COLUMN = "@@index"


def format_dataframe(df, case_id=constants.CASE_CONCEPT_NAME, activity_key=xes_constants.DEFAULT_NAME_KEY,
                     timestamp_key=xes_constants.DEFAULT_TIMESTAMP_KEY, timest_format=None):
    """
    Give the appropriate format on the dataframe, for process mining purposes

    Parameters
    --------------
    df
        Dataframe
    case_id
        Case identifier column
    activity_key
        Activity column
    timestamp_key
        Timestamp column
    timest_format
        Timestamp format that is provided to Pandas

    Returns
    --------------
    df
        Dataframe
    """
    import pandas as pd
    if case_id not in df.columns:
        raise Exception(case_id + " column (case ID) is not in the dataframe!")
    if activity_key not in df.columns:
        raise Exception(activity_key + " column (activity) is not in the dataframe!")
    if timestamp_key not in df.columns:
        raise Exception(timestamp_key + " column (timestamp) is not in the dataframe!")
    df = df.rename(columns={case_id: constants.CASE_CONCEPT_NAME, activity_key: xes_constants.DEFAULT_NAME_KEY,
                            timestamp_key: xes_constants.DEFAULT_TIMESTAMP_KEY})
    df[constants.CASE_CONCEPT_NAME] = df[constants.CASE_CONCEPT_NAME].astype(str)
    # makes sure that the timestamp column is of timestamp type
    df[xes_constants.DEFAULT_TIMESTAMP_KEY] = pd.to_datetime(df[xes_constants.DEFAULT_TIMESTAMP_KEY],
                                                             format=timest_format)
    # set an index column
    df = pandas_utils.insert_index(df, INDEX_COLUMN)
    # sorts the dataframe
    df = df.sort_values([constants.CASE_CONCEPT_NAME, xes_constants.DEFAULT_TIMESTAMP_KEY, INDEX_COLUMN])
    # logging.warning(
    #    "please convert the dataframe for advanced process mining applications. log = pm4py.convert_to_event_log(df)")
    return df
