from intervaltree import IntervalTree, Interval
from pm4py.objects.conversion.lifecycle_log import factory as lifecycle_factory
from pm4py.util import constants
from pm4py.objects.log.util import xes
from pm4py.objects.log.util import sorting

INSERT_AS_ATTRIBUTE = "insert_as_attribute"


def get_int_tree(log, parameters=None):
    """
    Gets a set of interval trees for a particular attribute (one interval tree per value)
    that aims to show how many intersections (contemporary work) are there for that attribute
    (activity/resource/station ...)

    Parameters
    ------------
    log
        Interval log (if not, it is automatically converted)
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    log
        Possibly transformed log
    dict_int_trees
        Dictionary of interval trees, one for each attribute value
    """
    if parameters is None:
        parameters = {}

    attribute_key = parameters[
        constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] if constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else xes.DEFAULT_NAME_KEY
    start_timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY in parameters else xes.DEFAULT_START_TIMESTAMP_KEY
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    insert_as_attribute = parameters[INSERT_AS_ATTRIBUTE] if INSERT_AS_ATTRIBUTE in parameters else True

    interval_log = lifecycle_factory.apply(log, variant=lifecycle_factory.TO_INTERVAL, parameters=parameters)
    interval_log = sorting.sort_timestamp_log(interval_log, start_timestamp_key)
    attribute_value_tree = {}

    for trace in interval_log:
        for event in trace:
            if attribute_key in event:
                value = event[attribute_key]
                start_timestamp = event[start_timestamp_key]
                complete_timestamp = event[timestamp_key]
                if complete_timestamp > start_timestamp:
                    if value not in attribute_value_tree:
                        attribute_value_tree[value] = IntervalTree()
                    attribute_value_tree[value].add(
                        Interval(start_timestamp.timestamp(), complete_timestamp.timestamp()))

    if insert_as_attribute:
        for trace in interval_log:
            for event in trace:
                if attribute_key in event:
                    value = event[attribute_key]
                    start_timestamp = event[start_timestamp_key]
                    complete_timestamp = event[timestamp_key]
                    if complete_timestamp > start_timestamp:
                        middle = (float(start_timestamp.timestamp()) + float(complete_timestamp.timestamp())) / 2.0
                        val = len(attribute_value_tree[value][middle])
                        event["@@int_tree_count_" + attribute_key] = val
                        event["@@int_tree_count_" + attribute_key + "_" + value] = val

    return log, attribute_value_tree
