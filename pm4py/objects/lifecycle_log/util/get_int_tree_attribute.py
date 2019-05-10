from intervaltree import IntervalTree, Interval
from pm4py.objects.conversion.lifecycle_log import factory as lifecycle_factory
from pm4py.util import constants
from pm4py.objects.log.util import xes


def get_int_tree(log, parameters=None):
    if parameters is None:
        parameters = {}

    attribute_key = parameters[
        constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] if constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else xes.DEFAULT_NAME_KEY
    start_timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY in parameters else xes.DEFAULT_START_TIMESTAMP_KEY
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    interval_log = lifecycle_factory.apply(log, variant=lifecycle_factory.TO_INTERVAL)
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

    return attribute_value_tree
