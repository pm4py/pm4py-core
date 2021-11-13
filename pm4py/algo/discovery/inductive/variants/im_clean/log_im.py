'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from enum import Enum

import pm4py
from pm4py.algo.discovery.dfg import algorithm as discover_dfg
from pm4py.algo.discovery.inductive.variants.im_clean.cuts import sequence as sequence_cut, xor as xor_cut, \
    concurrency as concurrent_cut, loop as loop_cut
from pm4py.algo.discovery.inductive.variants.im_clean.fall_throughs import activity_once_per_trace, activity_concurrent, \
    strict_tau_loop, tau_loop
from pm4py.algo.discovery.inductive.variants.im_clean.utils import __filter_dfg_on_threshold, __flower
from pm4py.algo.discovery.minimum_self_distance import algorithm as msd_algo
from pm4py.algo.discovery.minimum_self_distance import utils as msdw_algo
from pm4py.objects.dfg.utils import dfg_utils
from pm4py.objects.log.obj import EventLog
from pm4py.objects.log.util import log as log_util
from pm4py.objects.process_tree import obj as pt
from pm4py.statistics.end_activities.log import get as get_ends
from pm4py.statistics.start_activities.log import get as get_starters
from pm4py.util import constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def __inductive_miner(log, dfg, threshold, root, act_key, use_msd, remove_noise=False):
    tree = __inductive_miner_internal(log, dfg, threshold, root, act_key, use_msd, remove_noise)
    return tree


def __inductive_miner_internal(log, dfg, threshold, root, act_key, use_msd, remove_noise=False):
    alphabet = pm4py.get_event_attribute_values(log, act_key)
    if threshold > 0 and remove_noise:
        end_activities = get_ends.get_end_activities(log,
                                                     parameters={constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key})

        dfg = __filter_dfg_on_threshold(dfg, end_activities, threshold)

    original_length = len(log)
    log = pm4py.filter_log(lambda t: len(t) > 0, log)

    # revised EMPTYSTRACES
    if original_length - len(log) > original_length * threshold:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.XOR, root), threshold, act_key,
                                             [EventLog(), log],
                                             use_msd)

    start_activities = get_starters.get_start_activities(log, parameters={
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key})
    end_activities = get_ends.get_end_activities(log, parameters={constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key})

    if __is_base_case_act(log, act_key) or __is_base_case_silent(log):
        return __apply_base_case(log, root, act_key)
    pre, post = dfg_utils.get_transitive_relations(dfg, alphabet)
    cut = sequence_cut.detect(alphabet, pre, post)
    if cut is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.SEQUENCE, root), threshold, act_key,
                                             sequence_cut.project(log, cut, act_key), use_msd)
    cut = xor_cut.detect(dfg, alphabet)
    if cut is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.XOR, root), threshold, act_key,
                                             xor_cut.project(log, cut, act_key), use_msd)
    cut = concurrent_cut.detect(dfg, alphabet, start_activities, end_activities,
                                msd=msdw_algo.derive_msd_witnesses(log, msd_algo.apply(log, parameters={
                                    constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}), parameters={
                                    constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}) if use_msd else None)
    if cut is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.PARALLEL, root), threshold, act_key,
                                             concurrent_cut.project(log, cut, act_key), use_msd)
    cut = loop_cut.detect(dfg, alphabet, start_activities, end_activities)
    if cut is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.LOOP, root), threshold, act_key,
                                             loop_cut.project(log, cut, act_key), use_msd)

    aopt = activity_once_per_trace.detect(log, alphabet, act_key)
    if aopt is not None:
        operator = pt.ProcessTree(operator=pt.Operator.PARALLEL, parent=root)
        operator.children.append(pt.ProcessTree(operator=None, parent=operator, label=aopt))
        return __add_operator_recursive_logs(operator, threshold, act_key,
                                             activity_once_per_trace.project(log, aopt, act_key), use_msd)
    act_conc = activity_concurrent.detect(log, alphabet, act_key, use_msd)
    if act_conc is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.PARALLEL, root), threshold, act_key,
                                             activity_concurrent.project(log, act_conc, act_key), use_msd)
    stl = strict_tau_loop.detect(log, start_activities, end_activities, act_key)
    if stl is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.LOOP, root), threshold, act_key,
                                             [stl, EventLog()],
                                             use_msd)
    tl = tau_loop.detect(log, start_activities, act_key)
    if tl is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.LOOP, root), threshold, act_key,
                                             [tl, EventLog()],
                                             use_msd)

    if threshold > 0 and not remove_noise:
        return __inductive_miner(log, dfg, threshold, root, act_key, use_msd, remove_noise=True)

    return __flower(alphabet, root)


def __add_operator_recursive_logs(operator, threshold, act_key, logs, use_msd):
    if operator.operator != pt.Operator.LOOP:
        for log in logs:
            operator.children.append(__inductive_miner(log, discover_dfg.apply(log, parameters={
                constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}), threshold, operator, act_key, use_msd))
    else:
        operator.children.append(__inductive_miner(logs[0], discover_dfg.apply(logs[0], parameters={
            constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}), threshold, operator, act_key, use_msd))
        logs = logs[1:]
        if len(logs) == 1:
            operator.children.append(__inductive_miner(logs[0], discover_dfg.apply(logs[0], parameters={
                constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}), threshold, operator, act_key, use_msd))
        else:
            operator.children.append(
                __add_operator_recursive_logs(
                    pt.ProcessTree(operator=pt.Operator.XOR, parent=operator), threshold, act_key, logs, use_msd))
    return operator


def __is_base_case_act(log, act_key):
    if len(list(filter(lambda t: len(t) == 1, log))) == len(log):
        if len(frozenset(log_util.get_event_labels(log, act_key))) == 1:
            return True
    return False


def __is_base_case_silent(log):
    return len(log) == 0


def __apply_base_case(log, root, act_key):
    if len(log) == 0:
        operator = pt.ProcessTree(parent=root)
        return operator
    else:
        operator = pt.ProcessTree(parent=root, label=log[0][0][act_key])
        return operator
