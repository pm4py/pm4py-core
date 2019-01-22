import itertools
from copy import deepcopy

import numpy as np

from pm4py.algo.other.decisiontree import get_log_representation
from pm4py.algo.other.decisiontree import log_transforming
from pm4py.algo.other.decisiontree import mine_decision_tree
from pm4py.objects.log.log import TraceLog

DEFAULT_MAX_REC_DEPTH_DEC_MINING = 2


def get_decision_mining_rules_given_activities(log, activities, parameters=None):
    """
    Performs rules discovery thanks to decision mining from a log and a list of activities

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
    rules
        Discovered rules leading to activities
    """
    clf, feature_names, classes, len_list_logs = perform_decision_mining_given_activities(
        log, activities, parameters=parameters)
    rules = get_rules_for_classes(clf, feature_names, classes, len_list_logs)

    return rules


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
    len_list_logs
        Length of each sublog considered
    """
    list_logs, considered_activities = log_transforming.get_log_traces_to_activities(log, activities,
                                                                                     parameters=parameters)

    classes = considered_activities
    target = []
    for i in range(len(list_logs)):
        target = target + [i] * len(list_logs[i])

    transf_log = TraceLog(list(itertools.chain.from_iterable(list_logs)))

    data, feature_names = get_log_representation.get_default_representation(transf_log)

    clf = mine_decision_tree.mine(data, target, max_depth=DEFAULT_MAX_REC_DEPTH_DEC_MINING)

    len_list_logs = [len(x) for x in list_logs]

    return clf, feature_names, classes, len_list_logs


def get_rules_for_classes(tree, feature_names, classes, len_list_logs, rec_depth=0, curr_node=0, rules=None,
                          curr_rec_rule=None):
    """
    Gets the rules that permits to go to a specific class

    Parameters
    -------------
    tree
        Decision tree
    feature_names
        Feature names for the decision tree
    classes
        Classes for the decision tree
    len_list_logs
        Length of each sublog
    rec_depth
        Recursion depth
    curr_node
        Node to consider in the decision tree
    rules
        Already established rules by the recursion algorithm
    curr_rec_rule
        Rule that the current recursion would like to add

    Returns
    -------------
    rules
        Rules that permits to go to each activity
    """
    if rules is None:
        rules = {}
    if curr_rec_rule is None:
        curr_rec_rule = []
    if rec_depth == 0:
        len_list_logs = [1.0 / (1.0 + np.log(x + 1)) for x in len_list_logs]
    feature = tree.tree_.feature[curr_node]
    feature_name = feature_names[feature]
    threshold = tree.tree_.threshold[curr_node]
    child_left = tree.tree_.children_left[curr_node]
    child_right = tree.tree_.children_right[curr_node]
    value = [a * b for a, b in zip(tree.tree_.value[curr_node][0], len_list_logs)]

    if child_left == child_right:
        target_class = classes[np.argmax(value)]
        if target_class not in rules:
            rules[target_class] = []
        rule_to_save = "(" + " && ".join(curr_rec_rule) + ")"
        rules[target_class].append(rule_to_save)
    else:
        if not child_left == curr_node and child_left >= 0:
            new_curr_rec_rule = form_new_curr_rec_rule(curr_rec_rule, False, feature_name, threshold)
            rules = get_rules_for_classes(tree, feature_names, classes, len_list_logs, rec_depth=rec_depth + 1,
                                          curr_node=child_left, rules=rules, curr_rec_rule=new_curr_rec_rule)
        if not child_right == curr_node and child_right >= 0:
            new_curr_rec_rule = form_new_curr_rec_rule(curr_rec_rule, True, feature_name, threshold)
            rules = get_rules_for_classes(tree, feature_names, classes, len_list_logs, rec_depth=rec_depth + 1,
                                          curr_node=child_right, rules=rules, curr_rec_rule=new_curr_rec_rule)
    if rec_depth == 0:
        for act in rules:
            rules[act] = " || ".join(rules[act])
    return rules


def form_new_curr_rec_rule(curr_rec_rule, positive, feature_name, threshold):
    """
    Adds a piece to the recursion rule we would like to add

    Parameters
    -------------
    curr_rec_rule
        Rule that the current recursion would like to add
    positive
        Indicate if we are going left/right in the tree
    feature_name
        Feature name of the current node
    threshold
        Threshold that leads to the current node

    Returns
    ------------
    new_rules
        Updated rules
    """
    new_rules = deepcopy(curr_rec_rule)

    if positive:
        if threshold == 0.5:
            new_rules.append(feature_name.replace("@", " == "))
        else:
            new_rules.append(feature_name + " <= " + str(threshold))
    else:
        if threshold == 0.5:
            new_rules.append(feature_name.replace("@", " != "))
        else:
            new_rules.append(feature_name + " > " + str(threshold))
    return new_rules
