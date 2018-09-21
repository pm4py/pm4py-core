from pm4py.entities.log.util import xes
from pm4py.util import constants
from pm4py.algo.filtering.common import filtering_constants

def apply(df, values, parameters=None):
    """
    Filter dataframe on attribute values

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    parameters
        Possible parameters of the algorithm, including:
            case_id_glue -> Case ID column in the dataframe
            attribute_key -> Attribute we want to filter
            positive -> Specifies if the filter should be applied including traces (positive=True) or excluding traces (positive=False)
    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else filtering_constants.CASE_CONCEPT_NAME
    attribute_key = parameters[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] if constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else xes.DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True

    return filter_df_on_attribute_values(df, values, case_id_glue=case_id_glue, attribute_key=attribute_key, positive=positive)

def get_attributes_count(df, attribute_key="concept:name"):
    """
    Return list of attributes contained in the specified column of the CSV

    Parameters
    -----------
    df
        Pandas dataframe
    attribute_key
        Attribute for which we want to known the values and the count

    Returns
    -----------
    attributes_values_dict
        Attributes in the specified column, along with their count
    """
    attributes_values_dict = dict(df[attribute_key].value_counts())
    return attributes_values_dict

def filter_df_on_attribute_values(df, values, case_id_glue="case:concept:name", attribute_key="concept:name", positive=True):
    """
    Filter dataframe on attribute values

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    case_id_glue
        Case ID column in the dataframe
    attribute_key
        Attribute we want to filter
    positive
        Specifies if the filtered should be applied including traces (positive=True) or excluding traces (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """
    if values is None:
        values = []
    filteredDfByEv = df[df[attribute_key].isin(values)]
    i1 = df.set_index(case_id_glue).index
    i2 = filteredDfByEv.set_index(case_id_glue).index
    if positive:
        return df[i1.isin(i2)]
    return df[~i1.isin(i2)]

def filter_df_keeping_specno_activities(df, activity_key="concept:name", max_no_activities=25):
    """
    Filter a dataframe on the specified number of attributes

    Parameters
    -----------
    df
        Dataframe
    activity_key
        Activity key in dataframe (must be specified if different from concept:name)
    max_no_activities
        Maximum allowed number of attributes

    Returns
    ------------
    df
        Filtered dataframe
    """
    activity_values_dict = dict(df[activity_key].value_counts())
    activity_values_ordered_list = []
    for act in activity_values_dict:
        activity_values_ordered_list.append([act, activity_values_dict[act]])
    activity_values_ordered_list = sorted(activity_values_ordered_list)
    # keep only a number of attributes <= max_no_activities
    activity_values_ordered_list = activity_values_ordered_list[0:min(len(activity_values_ordered_list), max_no_activities)]
    activity_to_keep = [x[0] for x in activity_values_ordered_list]
    df = df[df[activity_key].isin(activity_to_keep)]
    return df