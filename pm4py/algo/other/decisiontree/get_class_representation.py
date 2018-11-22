import numpy as np


def get_class_representation_by_str_ev_attr_value_presence(log, str_attr_name, str_attr_value):
    """
    Get the representation for the target part of the decision tree learning
    if the focus is on the presence of a given value of a (string) event attribute

    Parameters
    -------------
    log
        Trace log
    str_attr_name
        Attribute name to consider
    str_attr_value
        Attribute value to consider

    Returns
    -------------
    target
        Target part for decision tree learning
    classes
        Name of the classes, in order
    """
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
    """
    Get the representation for the target part of the decision tree learning
    if the focus is on all (string) values of an event attribute

    Parameters
    ------------
    log
        Trace log
    str_attr_name
        Attribute name to consider

    Returns
    ------------
    target
        Target part for decision tree learning
    classes
        Name of the classes, in order
    """
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