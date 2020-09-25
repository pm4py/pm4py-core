def to_dict_records(df):
    """
    Pandas dataframe to dictionary (records method)

    Parameters
    ---------------
    df
        Dataframe

    Returns
    --------------
    list_dictio
        List containing a dictionary for each row
    """
    return df.to_dict('records')


def to_dict_index(df):
    """
    Pandas dataframe to dictionary (index method)

    Parameters
    ---------------
    df
        Dataframe

    Returns
    --------------
    dict
        dict like {index -> {column -> value}}
    """
    return df.to_dict('index')
