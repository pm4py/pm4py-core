import numpy as np

from pm4py.algo.other.decisiontree import get_log_representation
from pm4py.algo.other.decisiontree import mine_decision_tree
from pm4py.objects.log.log import EventLog

DEFAULT_MAX_REC_DEPTH_DEC_MINING = 3


def get_data_classes(log1, log2, parameters=None):
    """
    Returns data and classes to infer the differences between the logs of the two periods

    Parameters
    ------------
    log1
        First log
    log2
        Second log
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    data
        Data
    feature_names
        Feature names
    target
        Target for each example
    classes
        Classes
    """

    if parameters is None:
        parameters = {}

    enable_succattr = parameters["enable_succattr"] if "enable_succattr" in parameters else False

    log = EventLog(list(log1) + list(log2))

    data, feature_names = get_log_representation.get_default_representation(log, enable_succattr=enable_succattr)

    target = np.array([0] * len(log1) + [1] * len(log2))
    classes = ["before", "after"]

    return data, feature_names, target, classes


def get_decision_tree(log1, log2, parameters=None):
    """
    Returns the decision tree representing the differences between the logs of the two periods

    Parameters
    ------------
    log1
        First log
    log2
        Second log
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    clf
        Decision tree
    feature_names
        Names of the features
    classes
        Classes (before, after)
    """

    data, feature_names, target, classes = get_data_classes(log1, log2, parameters=parameters)

    clf = mine_decision_tree.mine(data, target, max_depth=DEFAULT_MAX_REC_DEPTH_DEC_MINING)

    return clf, feature_names, classes
