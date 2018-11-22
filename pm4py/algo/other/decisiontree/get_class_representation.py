import numpy as np


def get_class_representation_by_str_ev_attr_value_presence(log, str_attr_name, str_attr_value):
    count = 0
    dictionary = {}
    target = []
    classes = []

    for trace in log:
        value = False
        for event in trace:
            if str_attr_name in event and event[str_attr_name] == str_attr_value:
                value = True
        if not str(value) in dictionary:
            dictionary[str(value)] = count
            classes.append(str(value))
            count = count + 1
        target.append(dictionary[str(value)])

    target = np.array(target)
    return target, classes


def get_class_representation_by_str_ev_attr_value_value(log, str_attr_name):
    count = 0
    dictionary = {}
    target = []
    classes = []

    for trace in log:
        value = "UNDEFINED"
        for event in trace:
            if str_attr_name in event and event[str_attr_name]:
                value = event[str_attr_name]
        if not str(value) in dictionary:
            dictionary[str(value)] = count
            classes.append(str(value))
            count = count + 1
        target.append(dictionary[str(value)])

    target = np.array(target)
    return target, classes