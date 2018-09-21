def apply(df, values, case_id_glue="case:concept:name", activity_key="concept:name", positive=True):
    """
    Filter dataframe on end activities

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
    return filter_df_on_end_activities(df, values, case_id_glue="case:concept:name", activity_key="concept:name", positive=True)

def get_end_activities(df, case_id_glue="case:concept:name", activity_key="concept:name"):
    """
    Get end activities count

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
    endact_dict
        Dictionary of end activities along with their count
    """
    lastEveDf = df.groupby(case_id_glue).last()
    endact_dict = dict(lastEveDf[activity_key].value_counts())
    return endact_dict

def filter_df_on_end_activities(df, values, case_id_glue="case:concept:name", activity_key="concept:name", positive=True):
    """
    Filter dataframe on end activities

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
    lastEveDf = df.groupby(case_id_glue).last()
    lastEveDf = lastEveDf[lastEveDf[activity_key].isin(values)]
    i1 = df.set_index(case_id_glue).index
    i2 = lastEveDf.index
    if positive:
        return df[i1.isin(i2)]
    return df[~i1.isin(i2)]

def filter_df_on_end_activities_nocc(df, nocc, ea_count=None, case_id_glue="case:concept:name", activity_key="concept:name"):
    """
    Filter dataframe on end activities number of occurrences

    Parameters
    -----------
    df
        Dataframe
    nocc
        Minimum number of occurrences of the end activity
    ea_count
        (if provided) Dictionary that associates each end activity with its count
    case_id_glue
        Column that contains the Case ID
    activity_key
        Column that contains the activity
    """
    firstEveDf = df.groupby(case_id_glue).last()
    if ea_count is None:
        ea_count = get_end_activities(df)
    ea_count = [k for k, v in ea_count.items() if v >= nocc]
    firstEveDf = firstEveDf[firstEveDf[activity_key].isin(ea_count)]
    i1 = df.set_index(case_id_glue).index
    i2 = firstEveDf.index
    return df[i1.isin(i2)]