def get_resources_from_df(social_df):
    """
    Gets the resource set list from the Social Network dataframe

    Parameters
    -------------
    social_df
        Social Network dataframe (basic or full matrix)

    Returns
    -------------
    resources_set
        Set of resources contained in the dataframe
    """
    unique_resources = social_df['resource'].unique()
    unique_next_resources = social_df['next_resource'].unique()
    return set(unique_resources) | set(unique_next_resources)


def get_activities_from_df(social_df):
    """
    Gets the activity set list from the Social Network dataframe

    Parameters
    ------------
    social_df
        Social Network dataframe (only full matrix)

    Returns
    -------------
    resources_set
        Set of resources contained in the dataframe
    """
    unique_activities = social_df['activity'].unique()
    unique_next_activities = social_df['next_activity'].unique()
    return set(unique_activities) | set(unique_next_activities)
