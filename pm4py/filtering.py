import pandas as pd
from pm4py.util import constants, xes_constants


def check_dataframe_columns(df):
    """
    Checks if the dataframe contains all the required columns.
    If not, raise an exception

    Parameters
    --------------
    df
        Pandas dataframe
    """
    if len(set(df.columns).intersection(
            set([constants.CASE_CONCEPT_NAME, xes_constants.DEFAULT_NAME_KEY,
                 xes_constants.DEFAULT_TIMESTAMP_KEY]))) < 3:
        raise Exception(
            "please format your dataframe accordingly! df = pm4py.format_dataframe(df, case_id='<name of the case ID column>', activity_key='<name of the activity column>', timestamp_key='<name of the timestamp column>')")


def filter_start_activities(log, admitted_start_activities):
    """
    Filter cases having a start activity in the provided list

    Parameters
    --------------
    log
        Log object
    admitted_start_activities
        List of admitted start activities

    Returns
    --------------
    filtered_log
        Filtered log object
    """
    if type(log) is pd.DataFrame:
        check_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.start_activities import start_activities_filter
        return start_activities_filter.apply(log, admitted_start_activities)
    else:
        from pm4py.algo.filtering.log.start_activities import start_activities_filter
        return start_activities_filter.apply(log, admitted_start_activities)


def filter_end_activities(log, admitted_end_activities):
    """
    Filter cases having an end activity in the provided list

    Parameters
    ---------------
    log
        Log object
    admitted_end_activities
        List of admitted end activities

    Returns
    ---------------
    filtered_log
        Filtered log object
    """
    if type(log) is pd.DataFrame:
        check_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.end_activities import end_activities_filter
        return end_activities_filter.apply(log, admitted_end_activities)
    else:
        from pm4py.algo.filtering.log.end_activities import end_activities_filter
        return end_activities_filter.apply(log, admitted_end_activities)


def filter_attribute_values(log, attribute, values, how="cases", positive=True):
    """
    Filter a log object on the values of some attribute

    Parameters
    --------------
    log
        Log object
    attribute
        Attribute to filter
    values
        Admitted (or forbidden) values
    how
        Specifies how the filter should be applied (cases filters the cases where at least one occurrence happens,
        events filter the events eventually trimming the cases)
    positive
        Specified if the values should be kept or removed

    Returns
    --------------
    filtered_log
        Filtered log object
    """
    if type(log) is pd.DataFrame:
        check_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.attributes import attributes_filter
        if how == "events":
            return attributes_filter.apply_events(log, values,
                                                  parameters={constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: attribute,
                                                              attributes_filter.Parameters.POSITIVE: positive})
        elif how == "cases":
            return attributes_filter.apply(log, values, parameters={
                constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: attribute, attributes_filter.Parameters.POSITIVE: positive})
    else:
        from pm4py.algo.filtering.log.attributes import attributes_filter
        if how == "events":
            return attributes_filter.apply_events(log, values,
                                                  parameters={constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: attribute,
                                                              attributes_filter.Parameters.POSITIVE: positive})
        else:
            return attributes_filter.apply(log, values, parameters={
                constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: attribute, attributes_filter.Parameters.POSITIVE: positive})


def filter_variants(log, admitted_variants):
    """
    Filter a log on a specified set of variants

    Parameters
    ---------------
    log
        Event log
    admitted_variants
        List of variants to filter

    Returns
    --------------
    filtered_log
        Filtered log object
    """
    if type(log) is pd.DataFrame:
        check_dataframe_columns(log)
        from pm4py.algo.filtering.pandas.variants import variants_filter
        return variants_filter.apply(log, admitted_variants)
    else:
        from pm4py.algo.filtering.log.variants import variants_filter
        return variants_filter.apply(log, admitted_variants)


def filter_variants_percentage(log, percentage=0.8):
    """
    Filter a log on the percentage of variants

    Parameters
    ---------------
    log
        Event log
    percentage
        Percentage of admitted variants

    Returns
    --------------
    filtered_log
        Filtered log object
    """
    if type(log) is pd.DataFrame:
        raise Exception(
            "filtering variants percentage on Pandas dataframe is currently not available! please convert the dataframe to event log with the method: log =  pm4py.convert_to_event_log(df)")
    else:
        from pm4py.algo.filtering.log.variants import variants_filter
        return variants_filter.filter_log_variants_percentage(log, percentage=percentage)
