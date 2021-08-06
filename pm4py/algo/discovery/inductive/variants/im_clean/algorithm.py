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
from typing import Union, Dict, Any, Optional, Tuple

import pandas as pd

import pm4py
from pm4py.algo.discovery.dfg import algorithm as discover_dfg
from pm4py.algo.discovery.inductive.util import tree_consistency
from pm4py.algo.discovery.inductive.variants.im_clean.cuts import sequence as sequence_cut, xor as xor_cut, \
    concurrency as concurrent_cut, loop as loop_cut
from pm4py.algo.discovery.inductive.variants.im_clean.fall_throughs import activity_once_per_trace, activity_concurrent, \
    strict_tau_loop, tau_loop
from pm4py.algo.discovery.minimum_self_distance import algorithm as msd_algo
from pm4py.algo.discovery.minimum_self_distance import utils as msdw_algo
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.conversion.process_tree import converter as tree_converter
from pm4py.objects.dfg.utils import dfg_utils
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.log.util import log as log_util
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree import obj as pt
from pm4py.objects.process_tree.utils import generic
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.statistics.end_activities.log import get as get_ends
from pm4py.statistics.start_activities.log import get as get_starters
from pm4py.util import constants, exec_utils, xes_constants
from pm4py.util import variants_util
from pm4py.objects.log.util import filtering_utils
import math


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    NOISE_THRESHOLD = 'noise_threshold'
    DFG_ONLY = 'dfg_only'
    USE_MSD_PARALLEL_CUT = 'use_msd_par_cut'


def apply(event_log: Union[pd.DataFrame, EventLog, EventStream],
          parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[PetriNet, Marking, Marking]:
    if parameters is None:
        parameters = {}
    tree = apply_tree(event_log, parameters=parameters)
    net, im, fm = tree_converter.apply(tree, variant=tree_converter.Variants.TO_PETRI_NET, parameters=parameters)
    return net, im, fm


def apply_variants(variants, parameters=None):
    if parameters is None:
        parameters = {}
    tree = apply_tree_variants(variants, parameters=parameters)
    net, im, fm = tree_converter.apply(tree, variant=tree_converter.Variants.TO_PETRI_NET, parameters=parameters)
    return net, im, fm


def apply_tree_variants(variants, parameters=None):
    if parameters is None:
        parameters = {}

    log = EventLog()
    threshold = exec_utils.get_param_value(Parameters.NOISE_THRESHOLD, parameters, 0.0)

    var_keys = list(variants.keys())
    for var in var_keys:
        val = variants[var]
        if type(val) is list:
            val = len(val)
        if threshold == 0.0:
            # the inductive miner without noise needs only 1 trace per variant
            val = 1
        for i in range(val):
            trace = variants_util.variant_to_trace(var, parameters=parameters)
            log.append(trace)

    return apply_tree(log, parameters=parameters)


def apply_tree(event_log: Union[pd.DataFrame, EventLog, EventStream],
               parameters: Optional[Dict[Union[Parameters, str], Any]] = None) -> ProcessTree:
    if parameters is None:
        parameters = {}
    event_log = log_converter.apply(event_log, parameters=parameters)
    if type(event_log) is not EventLog:
        raise ValueError('input argument log should be of type pandas.DataFrame, Event Log or Event Stream')
    act_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY.value, parameters,
                                         xes_constants.DEFAULT_NAME_KEY)

    if exec_utils.get_param_value(Parameters.DFG_ONLY, parameters, False):
        event_log = None

    threshold = exec_utils.get_param_value(Parameters.NOISE_THRESHOLD, parameters, 0.0)

    if threshold == 0.0:
        # keep one trace per variant; more performant
        event_log = filtering_utils.keep_one_trace_per_variant(event_log, parameters=parameters)

    tree = inductive_miner(event_log, discover_dfg.apply(event_log, parameters={
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}),
                           threshold, None,
                           act_key, exec_utils.get_param_value(Parameters.USE_MSD_PARALLEL_CUT, parameters, True))

    tree_consistency.fix_parent_pointers(tree)
    tree = generic.fold(tree)
    generic.tree_sort(tree)

    return tree


def inductive_miner(log, dfg, threshold, root, act_key, use_msd, remove_noise=False):
    alphabet = pm4py.get_event_attribute_values(log, act_key)
    if threshold > 0 and remove_noise:
        end_activities = get_ends.get_end_activities(log,
                                                     parameters={constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key})
        outgoing_max_occ = {}
        for x, y in dfg.items():
            act = x[0]
            if act not in outgoing_max_occ:
                outgoing_max_occ[act] = y
            else:
                outgoing_max_occ[act] = max(y, outgoing_max_occ[act])
            if act in end_activities:
                outgoing_max_occ[act] = max(outgoing_max_occ[act], end_activities[act])
        dfg_list = sorted([(x, y) for x, y in dfg.items()], key=lambda x: (x[1], x[0]), reverse=True)
        dfg_list = [x for x in dfg_list if x[1] > threshold * outgoing_max_occ[x[0][0]]]
        dfg_list = [x[0] for x in dfg_list]
        # filter the elements in the DFG
        dfg = {x: y for x, y in dfg.items() if x in dfg_list}

    original_length = len(log)
    log = pm4py.filter_log(lambda t: len(t) > 0, log)

    # revised EMPTYSTRACES
    if original_length - len(log) > original_length * threshold:
        return _add_operator_recursive(pt.ProcessTree(pt.Operator.XOR, root), threshold, act_key, [EventLog(), log],
                                       use_msd)

    start_activities = get_starters.get_start_activities(log, parameters={
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key})
    end_activities = get_ends.get_end_activities(log, parameters={constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key})

    if _is_base_case_act(log, act_key) or _is_base_case_silent(log):
        return _apply_base_case(log, root, act_key)
    pre, post = dfg_utils.get_transitive_relations(dfg, alphabet)
    cut = sequence_cut.detect(alphabet, pre, post)
    if cut is not None:
        return _add_operator_recursive(pt.ProcessTree(pt.Operator.SEQUENCE, root), threshold, act_key,
                                       sequence_cut.project(log, cut, act_key), use_msd)
    cut = xor_cut.detect(dfg, alphabet)
    if cut is not None:
        return _add_operator_recursive(pt.ProcessTree(pt.Operator.XOR, root), threshold, act_key,
                                       xor_cut.project(log, cut, act_key), use_msd)
    cut = concurrent_cut.detect(dfg, alphabet, start_activities, end_activities,
                                msd=msdw_algo.derive_msd_witnesses(log, msd_algo.apply(log, parameters={
                                    constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}), parameters={
                                    constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}) if use_msd else None)
    if cut is not None:
        return _add_operator_recursive(pt.ProcessTree(pt.Operator.PARALLEL, root), threshold, act_key,
                                       concurrent_cut.project(log, cut, act_key), use_msd)
    cut = loop_cut.detect(dfg, alphabet, start_activities, end_activities)
    if cut is not None:
        return _add_operator_recursive(pt.ProcessTree(pt.Operator.LOOP, root), threshold, act_key,
                                       loop_cut.project(log, cut, act_key), use_msd)

    aopt = activity_once_per_trace.detect(log, alphabet, act_key)
    if aopt is not None:
        operator = pt.ProcessTree(operator=pt.Operator.PARALLEL, parent=root)
        operator.children.append(pt.ProcessTree(operator=None, parent=operator, label=aopt))
        return _add_operator_recursive(operator, threshold, act_key,
                                       activity_once_per_trace.project(log, aopt, act_key), use_msd)
    act_conc = activity_concurrent.detect(log, alphabet, act_key, use_msd)
    if act_conc is not None:
        return _add_operator_recursive(pt.ProcessTree(pt.Operator.PARALLEL, root), threshold, act_key,
                                       activity_concurrent.project(log, act_conc, act_key), use_msd)
    stl = strict_tau_loop.detect(log, start_activities, end_activities, act_key)
    if stl is not None:
        return _add_operator_recursive(pt.ProcessTree(pt.Operator.LOOP, root), threshold, act_key, [stl, EventLog()],
                                       use_msd)
    tl = tau_loop.detect(log, start_activities, act_key)
    if tl is not None:
        return _add_operator_recursive(pt.ProcessTree(pt.Operator.LOOP, root), threshold, act_key, [tl, EventLog()],
                                       use_msd)

    if threshold > 0 and not remove_noise:
        return inductive_miner(log, dfg, threshold, root, act_key, use_msd, remove_noise=True)

    return _flower(alphabet, root)


def _flower(alphabet, root):
    operator = pt.ProcessTree(operator=pt.Operator.LOOP, parent=root)
    operator.children.append(pt.ProcessTree(parent=operator))
    xor = pt.ProcessTree(operator=pt.Operator.XOR)
    operator.children.append(xor)
    for a in alphabet:
        xor.children.append(pt.ProcessTree(label=a, parent=xor))
    return operator


def _is_base_case_act(log, act_key):
    if len(list(filter(lambda t: len(t) == 1, log))) == len(log):
        if len(frozenset(log_util.get_event_labels(log, act_key))) == 1:
            return True
    return False


def _is_base_case_silent(log):
    return len(log) == 0


def _apply_base_case(log, root, act_key):
    if len(log) == 0:
        operator = pt.ProcessTree(parent=root)
        return operator
    else:
        operator = pt.ProcessTree(parent=root, label=log[0][0][act_key])
        return operator


def _add_operator_recursive(operator, threshold, act_key, logs, use_msd):
    if operator.operator != pt.Operator.LOOP:
        for log in logs:
            operator.children.append(inductive_miner(log, discover_dfg.apply(log, parameters={
                constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}), threshold, operator, act_key, use_msd))
    else:
        operator.children.append(inductive_miner(logs[0], discover_dfg.apply(logs[0], parameters={
            constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}), threshold, operator, act_key, use_msd))
        logs = logs[1:]
        if len(logs) == 1:
            operator.children.append(inductive_miner(logs[0], discover_dfg.apply(logs[0], parameters={
                constants.PARAMETER_CONSTANT_ACTIVITY_KEY: act_key}), threshold, operator, act_key, use_msd))
        else:
            operator.children.append(
                _add_operator_recursive(
                    pt.ProcessTree(operator=pt.Operator.XOR, parent=operator), threshold, act_key, logs, use_msd))
    return operator
