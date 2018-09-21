from pm4py.algo.filtering.common.start_activities import start_activities_common

def apply(df, values, parameters=None):
    """
    Filter dataframe on start activities

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    parameters
        Possible parameters of the algorithm, including:
            case_id_glue -> Case ID column in the dataframe
            activity_key -> Column that represents the activity
            positive -> Specifies if the filtered should be applied including traces (positive=True) or excluding traces (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}
    case_id_glue = parameters["case_id_glue"] if "case_id_glue" in parameters else "case:concept:name"
    activity_key = parameters["activity_key"] if "activity_key" in parameters else "concept:name"
    positive = parameters["positive"] if "positive" in parameters else True
    
    return filter_df_on_start_activities(df, values, case_id_glue=case_id_glue, activity_key=activity_key, positive=positive)

def get_start_activities(df, case_id_glue="case:concept:name", activity_key="concept:name"):
    """
    Get start activities count

    Parameters
    -----------
    df
        Pandas dataframe
    case_id_glue
        Column that identifies the case ID
    activity_key
        Column that identifies the activity

    Returns
    -----------
    startact_dict
        Dictionary of start activities along with their count
    """
    firstEveDf = df.groupby(case_id_glue).first()
    startact_dict = dict(firstEveDf[activity_key].value_counts())
    return startact_dict

def filter_df_on_start_activities(df, values, case_id_glue="case:concept:name", activity_key="concept:name", positive=True):
    """
    Filter dataframe on start activities

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    case_id_glue
        Case ID column in the dataframe
    activity_key
        Column that represent the activity
    positive
        Specifies if the filtered should be applied including traces (positive=True) or excluding traces (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """
    firstEveDf = df.groupby(case_id_glue).first()
    firstEveDf = firstEveDf[firstEveDf[activity_key].isin(values)]
    i1 = df.set_index(case_id_glue).index
    i2 = firstEveDf.index
    if positive:
        return df[i1.isin(i2)]
    return df[~i1.isin(i2)]

def filter_df_on_start_activities_nocc(df, nocc, sa_count=None, case_id_glue="case:concept:name", activity_key="concept:name"):
    """
    Filter dataframe on start activities number of occurrences

    Parameters
    -----------
    df
        Dataframe
    nocc
        Minimum number of occurrences of the start activity
    sa_count
        (if provided) Dictionary that associates each start activity with its count
    case_id_glue
        Column that contains the Case ID
    activity_key
        Column that contains the activity

    Returns
    ------------
    df
        Filtered dataframe
    """
    firstEveDf = df.groupby(case_id_glue).first()
    if sa_count is None:
        sa_count = get_start_activities(df)
    sa_count = [k for k, v in sa_count.items() if v >= nocc]
    firstEveDf = firstEveDf[firstEveDf[activity_key].isin(sa_count)]
    i1 = df.set_index(case_id_glue).index
    i2 = firstEveDf.index
    return df[i1.isin(i2)]