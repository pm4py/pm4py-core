from enum import Enum

import pm4py
from pm4py.algo.discovery.dfg import algorithm as discover_dfg
from pm4py.algo.discovery.inductive.variants.im_clean.cuts import sequence as sequence_cut, xor as xor_cut, \
    concurrency as concurrent_cut, loop as loop_cut, sequence_strict as sequence_strict_cut
from pm4py.algo.discovery.inductive.variants.im_clean.fall_throughs import activity_once_per_trace, activity_concurrent, \
    strict_tau_loop, tau_loop
from pm4py.algo.discovery.inductive.variants.im_clean.utils import __filter_dfg_on_threshold, __flower
from pm4py.algo.discovery.inductive.variants.im_clean import utils as imut
from pm4py.objects.dfg.utils import dfg_utils
from pm4py.objects.process_tree import obj as pt
from pm4py.util import constants
from pm4py.util.compression import util as compression

class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def __inductive_miner(log, dfg, threshold, root, use_msd, remove_noise=False):
    tree = __inductive_miner_internal(
        log, dfg, threshold, root, use_msd, remove_noise)
    return tree


def __inductive_miner_internal(log, dfg, threshold, root, use_msd, remove_noise=False):
    alphabet = compression.get_alphabet(log)
    if threshold > 0 and remove_noise:
        end_activities = compression.get_end_activities(log)
        dfg = __filter_dfg_on_threshold(dfg, end_activities, threshold)

    original_length = len(log)
    log = list(filter(lambda t: len(t) > 0, log))
    
    # revised EMPTYSTRACES
    if original_length - len(log) > original_length * threshold:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.XOR, root), threshold, [[], log], use_msd)

    start_activities = compression.get_start_activities(log)
    end_activities = compression.get_end_activities(log)

    if __is_base_case_act(log) or __is_base_case_silent(log):
        return __apply_base_case(log, root)
    pre, post = dfg_utils.get_transitive_relations(dfg, alphabet)
    cut = sequence_strict_cut.detect(alphabet, pre, post, dfg, start_activities,end_activities)
    if cut is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.SEQUENCE, root), threshold,
                                             sequence_cut.project(log, cut), use_msd)
    cut = xor_cut.detect(dfg, alphabet)
    if cut is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.XOR, root), threshold,
                                             xor_cut.project(log, cut), use_msd)
    cut = concurrent_cut.detect(dfg, alphabet, start_activities, end_activities, msd=imut.msdw(
        log, imut.msd(log)) if use_msd else None)
    if cut is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.PARALLEL, root), threshold,
                                             concurrent_cut.project(log, cut), use_msd)
    cut = loop_cut.detect(dfg, alphabet, start_activities, end_activities)
    if cut is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.LOOP, root), threshold,
                                             loop_cut.project(log, cut), use_msd)

    aopt = activity_once_per_trace.detect(log, alphabet)
    if aopt is not None:
        operator = pt.ProcessTree(operator=pt.Operator.PARALLEL, parent=root)
        operator.children.append(pt.ProcessTree(
            operator=None, parent=operator, label=aopt))
        return __add_operator_recursive_logs(operator, threshold, activity_once_per_trace.project(log, aopt), use_msd)
    act_conc = activity_concurrent.detect(log, alphabet, use_msd)
    if act_conc is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.PARALLEL, root), threshold,
                                             activity_concurrent.project(log, act_conc), use_msd)
    stl = strict_tau_loop.detect(
        log, start_activities, end_activities)
    if stl is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.LOOP, root), threshold, [stl, []], use_msd)
    tl = tau_loop.detect(log, start_activities)
    if tl is not None:
        return __add_operator_recursive_logs(pt.ProcessTree(pt.Operator.LOOP, root), threshold, [tl, []], use_msd)

    if threshold > 0 and not remove_noise:
        return __inductive_miner(log, dfg, threshold, root, use_msd, remove_noise=True)

    return __flower(alphabet, root)


def __add_operator_recursive_logs(operator, threshold, logs, use_msd):
    if operator.operator != pt.Operator.LOOP:
        for log in logs:
            operator.children.append(__inductive_miner(
                log, compression.discover_dfg(log), threshold, operator, use_msd))
    else:
        operator.children.append(__inductive_miner(
            logs[0], compression.discover_dfg(logs[0]), threshold, operator, use_msd))
        logs = logs[1:]
        if len(logs) == 1:
            operator.children.append(__inductive_miner(
                logs[0], compression.discover_dfg(logs[0]), threshold, operator, use_msd))
        else:
            operator.children.append(
                __add_operator_recursive_logs(
                    pt.ProcessTree(operator=pt.Operator.XOR, parent=operator), threshold, logs, use_msd))
    return operator


def __is_base_case_act(log):
    return True if len(list(filter(lambda t: len(t) == 1, log))) == len(log) and len(compression.get_alphabet(log)) == 1 else False


def __is_base_case_silent(log):
    return len(log) == 0


def __apply_base_case(log, root):
    return pt.ProcessTree(parent=root) if len(log) == 0 else pt.ProcessTree(parent=root, label=log[0][0])
