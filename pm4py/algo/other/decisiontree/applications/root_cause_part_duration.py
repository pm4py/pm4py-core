import numpy as np

from pm4py.algo.other.decisiontree import get_log_representation
from pm4py.algo.other.decisiontree import log_transforming
from pm4py.algo.other.decisiontree import mine_decision_tree


def perform_duration_root_cause_analysis(log, activity, parameters=None):
    """
    Perform root cause analysis about the excessive duration of an activity

    Parameters
    -------------
    log
        Trace log
    activity
        Activity
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    clf
        Decision tree
    feature_names
        Feature names
    classes
        Classes
    """
    transf_log, traces_interlapsed_time_to_act = log_transforming.get_log_traces_until_activity(log, activity,
                                                                                                parameters=parameters)
    thresh = log_transforming.get_first_quartile_times_interlapsed_in_activity(log, activity, parameters=parameters)
    data, feature_names = get_log_representation.get_default_representation(transf_log)
    classes = ["under", "over"]
    target = []
    for it in traces_interlapsed_time_to_act:
        if it <= thresh:
            target.append(0)
        else:
            target.append(1)
    target = np.array(target)
    clf = mine_decision_tree.mine(data, target)

    return clf, feature_names, classes
