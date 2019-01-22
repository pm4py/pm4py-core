import itertools

from pm4py.algo.other.decisiontree import get_log_representation
from pm4py.algo.other.decisiontree import log_transforming
from pm4py.algo.other.decisiontree import mine_decision_tree
from pm4py.objects.log.log import TraceLog


def perform_decision_mining_given_activities(log, activities, parameters=None):
    """
    Performs decision mining on the causes the leads to an exclusive choice of the activities

    Parameters
    -------------
    log
        Trace log
    activities
        List of activities to consider in decision mining
    parameters
        Possible parameters of the algorithm, including:
            PARAMETER_CONSTANT_ACTIVITY_KEY -> activity
            PARAMETER_CONSTANT_TIMESTAMP_KEY -> timestamp

    Returns
    -------------
    clf
        Decision tree
    feature_names
        Feature names
    classes
        Classes
    """
    list_logs, considered_activities = log_transforming.get_log_traces_to_activities(log, activities,
                                                                                     parameters=parameters)

    classes = considered_activities
    target = []
    for i in range(len(list_logs)):
        target = target + [i] * len(list_logs[i])

    transf_log = TraceLog(list(itertools.chain.from_iterable(list_logs)))

    data, feature_names = get_log_representation.get_default_representation(transf_log)

    clf = mine_decision_tree.mine(data, target)

    return clf, feature_names, classes
