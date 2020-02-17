from pm4py.statistics.attributes.common import get as attributes_common
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY


def get_attribute_values(df, attribute_key, parameters=None):
    """
    Return list of attribute values contained in the specified column of the CSV

    Parameters
    -----------
    df
        Pandas dataframe
    attribute_key
        Attribute for which we want to known the values and the count
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    attributes_values_dict
        Attributes in the specified column, along with their count
    """
    if parameters is None:
        parameters = {}
    str(parameters)
    attributes_values_dict = dict(df[attribute_key].value_counts())
    # print("attributes_values_dict=",attributes_values_dict)
    return attributes_values_dict


def get_kde_numeric_attribute(df, attribute, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values

    Parameters
    -------------
    df
        Pandas dataframe
    attribute
        Numeric attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    if parameters is None:
        parameters = {}

    max_no_of_points_to_sample = parameters[
        "max_no_of_points_to_sample"] if "max_no_of_points_to_sample" in parameters else 100000
    red_df = df.dropna(subset=[attribute])
    if len(red_df) > max_no_of_points_to_sample:
        red_df = red_df.sample(n=max_no_of_points_to_sample)
    values = list(red_df[attribute])

    return attributes_common.get_kde_numeric_attribute(values, parameters=parameters)


def get_kde_numeric_attribute_json(df, attribute, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values
    (expressed as JSON)

    Parameters
    --------------
    df
        Pandas dataframe
    attribute
        Numeric attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph

    Returns
    --------------
    json
        JSON representing the graph points
    """
    values = list(df.dropna(subset=[attribute])[attribute])

    return attributes_common.get_kde_numeric_attribute_json(values, parameters=parameters)


def get_kde_date_attribute(df, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values

    Parameters
    -------------
    df
        Pandas dataframe
    attribute
        Date attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    if parameters is None:
        parameters = {}

    max_no_of_points_to_sample = parameters[
        "max_no_of_points_to_sample"] if "max_no_of_points_to_sample" in parameters else 100000
    red_df = df.dropna(subset=[attribute])
    if len(red_df) > max_no_of_points_to_sample:
        red_df = red_df.sample(n=max_no_of_points_to_sample)
    date_values = list(red_df[attribute])
    return attributes_common.get_kde_date_attribute(date_values, parameters=parameters)


def get_kde_date_attribute_json(df, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values
    (expressed as JSON)

    Parameters
    --------------
    df
        Pandas dataframe
    attribute
        Date attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph

    Returns
    --------------
    json
        JSON representing the graph points
    """
    values = list(df.dropna(subset=[attribute])[attribute])

    return attributes_common.get_kde_date_attribute_json(values, parameters=parameters)
