from copy import copy

import numpy as np
import pandas as pd

from pm4py.algo.filtering.log.attributes import attributes_filter as log_attributes_filter
from pm4py.algo.filtering.pandas.attributes import attributes_filter as pd_attributes_filter
from pm4py.objects.conversion.log import factory as conversion_factory
from pm4py.objects.log.log import EventStream
from pm4py.objects.log.util import xes
from pm4py.statistics.traces.log import case_statistics as log_case_statistics
from pm4py.statistics.traces.pandas import case_statistics as pd_case_statistics
from pm4py.util import constants

KEEP_UNIQUE = "keep_unique"
SKIP_LAST = "skip_last"


def get_variants_matrix_from_variants_list(variants_list, activities, parameters=None):
    """
    Gets a numeric matrix where each row is associated to a different set of activities
    happening in the (complete) variants of the log, along with the count of the particular
    situation

    Parameters
    -------------
    variants_list
        List of variants contained in the log, along with their count
    activities
        List of activities in the log
    parameters
        Parameters of the algorithm: keep_unique (default: True)

    Returns
    -------------
    variants_matrix
        Variants matrix of the log
    """
    if parameters is None:
        parameters = {}
    keep_unique = parameters[KEEP_UNIQUE] if KEEP_UNIQUE in parameters else True
    variants_mat = []
    for var in variants_list:
        variant = var[0].split(",")
        count = var[1]
        this_var_repr = [0] * len(activities)
        for act in variant:
            i = activities.index(act)
            this_var_repr[i] = this_var_repr[i] + count
        variants_mat.append(this_var_repr)
    variants_mat = np.asmatrix(variants_mat)
    if keep_unique:
        variants_mat = np.unique(variants_mat, axis=0)
    return variants_mat, activities


def get_prefix_repr(prefix, activities):
    """
    Gets the numeric representation (as vector) of a prefix

    Parameters
    -------------
    prefix
        Prefix
    activities
        Activities

    Returns
    -------------
    prefix_repr
        Representation of a prefix
    """
    this_pref_repr = [0] * len(activities)
    for act in prefix:
        i = activities.index(act)
        this_pref_repr[i] = this_pref_repr[i] + 1
    return tuple(this_pref_repr)


def get_prefix_matrix_from_variants_list(variants_list, activities, parameters=None):
    """
    Gets a numeric matrix where each row is associated to a different prefix of activities
    happening in the variants of the log, along with the count of the particular situation

    Parameters
    -------------
    variants_list
        List of variants contained in the log, along with their count
    activities
        List of activities in the log
    parameters
        Parameters of the algorithm

    Returns
    -------------
    prefix_mat
        Prefix matrix of the log
    """
    if parameters is None:
        parameters = {}
    skip_last = parameters[SKIP_LAST] if SKIP_LAST in parameters else False

    prefixes = {}
    for var in variants_list:
        variant = var[0].split(",")
        count = var[1]
        prefix = []
        for index, act in enumerate(variant):
            if skip_last and index == len(variant) - 1:
                break
            prefix.append(act)
            prefix_repr = get_prefix_repr(prefix, activities)
            if prefix_repr not in prefixes:
                prefixes[prefix_repr] = 0
            prefixes[prefix_repr] = prefixes[prefix_repr] + count
    prefix_mat = []
    for pref in prefixes:
        pref_list = copy(list(pref))
        for i in range(len(pref_list)):
            pref_list[i] = pref_list[i] * prefixes[pref]
        prefix_mat.append(pref_list)
    prefix_mat = np.asmatrix(prefix_mat)
    prefix_mat = np.unique(prefix_mat, axis=0)
    return prefix_mat, activities


def get_prefix_matrix_from_trace(trace, activities, parameters=None):
    """
    Gets a numeric matrix where a trace is associated to different rows, each one is
    referring to one of its prefixes.

    Parameters
    --------------
    trace
        Trace of the event log
    activities
        Activities
    parameters
        Parameters of the algorithm

    Returns
    --------------
    prefix_mat
        Prefix matrix of the log
    """
    if parameters is None:
        parameters = {}
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    skip_last = parameters[SKIP_LAST] if SKIP_LAST in parameters else False
    prefix_mat = []
    this_prefix_repr = [0] * len(activities)
    for index, event in enumerate(trace):
        if skip_last and index == len(trace) - 1:
            break
        eve_act = event[activity_key]
        eve_act_idx = activities.index(eve_act)
        this_prefix_repr[eve_act_idx] = this_prefix_repr[eve_act_idx] + 1
        prefix_mat.append(copy(this_prefix_repr))
    prefix_mat = np.asmatrix(prefix_mat)
    return prefix_mat


def get_prefix_matrix_from_var_str(var_str, activities, parameters=None):
    """
    Gets a numeric matrix where a variant is associated to different rows, each one is
    referring to one of its prefixes.

    Parameters
    --------------
    var_str
        String representation of a variant
    activities
        Activities
    parameters
        Parameters of the algorithm

    Returns
    --------------
    prefix_mat
        Prefix matrix of the log
    """
    if parameters is None:
        parameters = {}
    skip_last = parameters[SKIP_LAST] if SKIP_LAST in parameters else False
    prefix_mat = []
    this_prefix_repr = [0] * len(activities)
    variant = var_str.split(",")
    for index, act in enumerate(variant):
        if skip_last and index == len(variant) - 1:
            break
        eve_act_idx = activities.index(act)
        this_prefix_repr[eve_act_idx] = this_prefix_repr[eve_act_idx] + 1
        prefix_mat.append(copy(this_prefix_repr))
    prefix_mat = np.asmatrix(prefix_mat)
    return prefix_mat


def get_prefix_matrix_from_event_log_not_unique(event_log, activities, parameters=None):
    """
    Gets a numeric matrix where each trace is associated to different rows, each one is
    referring to one of its prefixes.

    Parameters
    --------------
    event_log
        Event log
    activities
        Activities
    parameters
        Parameters of the algorithm

    Returns
    --------------
    prefix_mat
        Prefix matrix of the log
    """
    if parameters is None:
        parameters = {}
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    skip_last = parameters[SKIP_LAST] if SKIP_LAST in parameters else False
    prefix_mat = []
    for trace in event_log:
        this_prefix_repr = [0] * len(activities)
        for index, event in enumerate(trace):
            if skip_last and index == len(trace) - 1:
                break
            eve_act = event[activity_key]
            eve_act_idx = activities.index(eve_act)
            this_prefix_repr[eve_act_idx] = this_prefix_repr[eve_act_idx] + 1
            prefix_mat.append(copy(this_prefix_repr))
    prefix_mat = np.asmatrix(prefix_mat)
    return prefix_mat, activities


def get_variants_list(log, parameters=None):
    """
    Gets the list of variants (along with their count) from the particular log type

    Parameters
    ------------
    log
        Log
    parameters
        Parameters of the algorithm

    Returns
    -------------
    variants_list
        List of variants of the log (along with their count)
    """
    variants_list = []
    if type(log) is pd.DataFrame:
        pd_variants = pd_case_statistics.get_variant_statistics(log, parameters=parameters)
        for var in pd_variants:
            varkeys = list(var.keys())
            del varkeys[varkeys.index("variant")]
            variants_list.append((var["variant"], var[varkeys[0]]))
    else:
        log_variants = log_case_statistics.get_variant_statistics(log, parameters=parameters)
        for var in log_variants:
            varkeys = list(var.keys())
            del varkeys[varkeys.index("variant")]
            variants_list.append((var["variant"], var[varkeys[0]]))
    return variants_list


def get_activities_list(log, parameters=None):
    """
    Gets the activities list from a log object, sorted by activity name

    Parameters
    --------------
    log
        Log
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    activities_list
        List of activities sorted by activity name
    """
    if parameters is None:
        parameters = {}
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    if type(log) is pd.DataFrame:
        activities = pd_attributes_filter.get_attribute_values(log, activity_key)
    else:
        activities = log_attributes_filter.get_attribute_values(log, activity_key)
    return sorted(list(activities.keys()))


def get_prefix_matrix(log, parameters=None):
    """
    Gets the prefix matrix from a log object

    Parameters
    --------------
    log
        Log
    parameters
        Parameters of the algorithm: activity_key

    Returns
    --------------
    prefix_matrix
        Prefix matrix
    activities
        Sorted (by name) activities of the log
    """
    if parameters is None:
        parameters = {}
    keep_unique = parameters[KEEP_UNIQUE] if KEEP_UNIQUE in parameters else False

    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = activity_key
    parameters[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = activity_key

    if type(log) is EventStream:
        log = conversion_factory.apply(log, parameters=parameters)
    variants_list = get_variants_list(log, parameters=parameters)
    activities = get_activities_list(log, parameters=parameters)

    if keep_unique:
        prefix_matrix, activities = get_prefix_matrix_from_variants_list(variants_list, activities,
                                                                         parameters=parameters)
    else:
        prefix_matrix, activities = get_prefix_matrix_from_event_log_not_unique(log, activities,
                                                                                parameters=parameters)

    return prefix_matrix, activities


def get_variants_matrix(log, parameters=None):
    """
    Gets the variants matrix from a log object

    Parameters
    -------------
    log
        Log
    parameters
        Parameters of the algorithm: activity_key

    Returns
    -------------
    variants_matrix
        Variants matrix
    activities
        Sorted (by name) activities of the log
    """
    if parameters is None:
        parameters = {}
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = activity_key
    parameters[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = activity_key

    if type(log) is EventStream:
        log = conversion_factory.apply(log, parameters=parameters)
    variants_list = get_variants_list(log, parameters=parameters)
    activities = get_activities_list(log, parameters=parameters)

    return get_variants_matrix_from_variants_list(variants_list, activities, parameters=parameters)


def get_prefix_variants_matrix(log, parameters=None):
    """
    Gets the prefix variants matrix from a log object

    Parameters
    -------------
    log
        Log
    parameters
        Parameters of the algorithm: activity_key

    Returns
    -------------
    prefix_matrix
        Prefix matrix
    variants_matrix
        Variants matrix
    activities
        Sorted (by name) activities of the log
    """
    if parameters is None:
        parameters = {}
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = activity_key
    parameters[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = activity_key

    if type(log) is EventStream:
        log = conversion_factory.apply(log, parameters=parameters)
    variants_list = get_variants_list(log, parameters=parameters)
    activities = get_activities_list(log, parameters=parameters)

    prefix_matrix, activities = get_prefix_matrix_from_variants_list(variants_list, activities, parameters=parameters)
    variants_matrix, activities = get_variants_matrix_from_variants_list(variants_list, activities,
                                                                         parameters=parameters)

    return prefix_matrix, variants_matrix, activities
