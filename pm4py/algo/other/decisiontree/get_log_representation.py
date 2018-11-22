import numpy as np

def get_string_trace_attribute_rep(trace, trace_attribute):
    if trace_attribute in trace:
        return "trace:" + str(trace_attribute) + "@" + str(trace[trace_attribute])
    return "trace:" + str(trace_attribute) + "@UNDEFINED"


def get_all_string_trace_attribute_values(log, trace_attribute):
    values = set()
    for trace in log:
        values.add(get_string_trace_attribute_rep(trace, trace_attribute))
    return list(sorted(values))


def get_string_event_attribute_rep(event, event_attribute):
    return "event:" + str(event_attribute) + "@" + str(event[event_attribute])


def get_values_event_attribute_for_trace(trace, event_attribute):
    values_trace = set()
    for event in trace:
        if event_attribute in event:
            values_trace.add(get_string_event_attribute_rep(event, event_attribute))
    if values_trace is None:
        values_trace.add("event:" + str(event_attribute) + "@UNDEFINED")
    return values_trace


def get_all_string_event_attribute_values(log, event_attribute):
    values = set()
    for trace in log:
        values = values.union(get_values_event_attribute_for_trace(trace, event_attribute))
    return list(sorted(values))


def get_numeric_trace_attribute_rep(trace_attribute):
    return "trace:" + trace_attribute


def get_numeric_trace_attribute_value(trace, trace_attribute):
    if trace_attribute in trace:
        return trace[trace_attribute]
    raise Exception("at least a trace without trace attribute: " + trace_attribute)


def get_numeric_event_attribute_rep(event_attribute):
    return "event:" + event_attribute


def get_numeric_event_attribute_value(event, event_attribute):
    if event_attribute in event:
        return event[event_attribute]
    return None


def get_numeric_event_attribute_value_trace(trace, event_attribute):
    non_zero_values = []
    for event in trace:
        value = get_numeric_event_attribute_value(event, event_attribute)
        if value is not None:
            non_zero_values.append(value)
    if len(non_zero_values) > 0:
        return non_zero_values[-1]
    raise Exception("at least a trace without any event with event attribute: " + event_attribute)


def get_representation(log, str_tr_attr, str_ev_attr, num_tr_attr, num_ev_attr):
    data = []
    feature_names = []
    count = 0
    dictionary = {}
    inv_dictionary = {}
    for trace_attribute in str_tr_attr:
        values = get_all_string_trace_attribute_values(log, trace_attribute)
        for value in values:
            dictionary[value] = count
            inv_dictionary[count] = value
            feature_names.append(value)
            count = count + 1
    for event_attribute in str_ev_attr:
        values = get_all_string_event_attribute_values(log, event_attribute)
        for value in values:
            dictionary[value] = count
            inv_dictionary[count] = value
            feature_names.append(value)
            count = count + 1
    for trace_attribute in num_tr_attr:
        dictionary[get_numeric_trace_attribute_rep(trace_attribute)] = count
        inv_dictionary[count] = value
        feature_names.append(value)
        count = count + 1
    for event_attribute in num_ev_attr:
        dictionary[get_numeric_event_attribute_rep(event_attribute)] = count
        inv_dictionary[count] = value
        feature_names.append(value)
        count = count + 1
    for trace in log:
        trace_rep = [0] * count
        for trace_attribute in str_tr_attr:
            trace_attr_rep = get_string_trace_attribute_rep(trace, trace_attribute)
            trace_rep[dictionary[trace_attr_rep]] = 1
        for event_attribute in str_ev_attr:
            values = get_values_event_attribute_for_trace(trace, event_attribute)
            for value in values:
                trace_rep[dictionary[value]] = 1
        for trace_attribute in num_tr_attr:
            trace_rep[dictionary[get_numeric_trace_attribute_rep(trace_attribute)]] = get_numeric_trace_attribute_value(
                trace, trace_attribute)
        for event_attribute in num_ev_attr:
            trace_rep[dictionary[
                get_numeric_event_attribute_rep(event_attribute)]] = get_numeric_event_attribute_value_trace(
                trace, event_attribute)
        data.append(trace_rep)
    data = np.asarray(data)
    return data, feature_names