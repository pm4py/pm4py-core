from pm4py.objects import log


def apply(df, parameters=None):
    """
    Converts a dataframe to an event log

    Parameters
    ----------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm

     Returns
    -------
    log : :class:`pm4py.log.log.EventLog`
        An event log
    """
    if parameters is None:
        parameters = {}

    return convert_dataframe_to_event_log(df)


def convert_dataframe_to_event_log(df):
    """
    Converts a dataframe to an event log

    Parameters
    ----------
    df
        Pandas dataframe

     Returns
    -------
    log : :class:`pm4py.log.log.EventLog`
        An event log
    """
    return log.log.EventLog(df.to_dict('records'), attributes={'origin': 'csv'})
