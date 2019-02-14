import numpy as np

from pm4py.algo.other.decisiontree import get_log_representation
from pm4py.algo.other.decisiontree import mine_decision_tree
from pm4py.objects.log.log import EventLog


def get_decision_tree(log1, log2, parameters=None):
    if parameters is None:
        parameters = {}

    enable_succattr = parameters["enable_succattr"] if "enable_succattr" in parameters else False

    log = EventLog(list(log1) + list(log2))
    print(log)

    data, feature_names = get_log_representation.get_default_representation(log, enable_succattr=enable_succattr)

    target = np.array([0] * len(log1) + [1] * len(log2))
    classes = ["before", "after"]

    clf = mine_decision_tree.mine(data, target)

    return clf, feature_names, classes
