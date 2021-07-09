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
import pkgutil

from pm4py import util as pmutil
from pm4py.algo.discovery.dfg.variants import native as dfg_inst
from pm4py.algo.discovery.inductive.util import shared_constants
from pm4py.algo.discovery.inductive.util import tree_consistency
from pm4py.algo.discovery.inductive.util.petri_el_count import Counts
from pm4py.algo.discovery.inductive.variants.im.util import get_tree_repr_implain
from pm4py.algo.discovery.inductive.variants.im_f.data_structures import subtree_infrequent as subtree
from pm4py.objects.conversion.log import converter
from pm4py.objects.conversion.process_tree import converter as tree_to_petri
from pm4py.objects.log.obj import EventLog
from pm4py.objects.log.util import filtering_utils
from pm4py.objects.process_tree.utils import generic
from pm4py.objects.process_tree.utils.generic import tree_sort
from pm4py.statistics.attributes.log import get as attributes_get
from pm4py.statistics.end_activities.log import get as end_activities_get
from pm4py.statistics.start_activities.log import get as start_activities_get
from pm4py.util import exec_utils
from pm4py.util import variants_util
from pm4py.util import xes_constants
import deprecation

from pm4py.util import constants
from enum import Enum


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    NOISE_THRESHOLD = "noiseThreshold"
    EMPTY_TRACE_KEY = "empty_trace"
    ONCE_PER_TRACE_KEY = "once_per_trace"
    CONCURRENT_KEY = "concurrent"
    STRICT_TAU_LOOP_KEY = "strict_tau_loop"
    TAU_LOOP_KEY = "tau_loop"


def apply(log, parameters):
    """
    Apply the IM_F algorithm to a log obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """

    if pkgutil.find_loader("pandas"):
        import pandas as pd
        from pm4py.statistics.variants.pandas import get as variants_get

        if type(log) is pd.DataFrame:
            vars = variants_get.get_variants_count(log, parameters=parameters)
            return apply_variants(vars, parameters=parameters)

    log = converter.apply(log, parameters=parameters)
    net, initial_marking, final_marking = tree_to_petri.apply(apply_tree(log, parameters))
    return net, initial_marking, final_marking


def apply_variants(variants, parameters=None):
    """
    Apply the IM_F algorithm to a dictionary of variants, obtaining a Petri net along with an initial and final marking

    Parameters
    -----------
    variants
        Variants
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    net, im, fm = tree_to_petri.apply(apply_tree_variants(variants, parameters=parameters))
    return net, im, fm


@deprecation.deprecated('2.2.10', '3.0.0', details='use newer IM implementation (IM_CLEAN)')
def apply_tree(log, parameters):
    """
    Apply the IM_FF algorithm to a log obtaining a process tree

    Parameters
    ----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    ----------
    process_tree
        Process tree
    """
    if parameters is None:
        parameters = {}

    if pkgutil.find_loader("pandas"):
        import pandas as pd
        from pm4py.statistics.variants.pandas import get as variants_get

        if type(log) is pd.DataFrame:
            vars = variants_get.get_variants_count(log, parameters=parameters)
            return apply_tree_variants(vars, parameters=parameters)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                              pmutil.xes_constants.DEFAULT_NAME_KEY)

    log = converter.apply(log, parameters=parameters)
    # keep only the activity attribute (since the others are not used)
    log = filtering_utils.keep_only_one_attribute_per_event(log, activity_key)

    noise_threshold = exec_utils.get_param_value(Parameters.NOISE_THRESHOLD, parameters,
                                                 shared_constants.NOISE_THRESHOLD_IMF)

    dfg = [(k, v) for k, v in dfg_inst.apply(log, parameters=parameters).items() if v > 0]
    c = Counts()
    activities = attributes_get.get_attribute_values(log, activity_key)
    start_activities = list(start_activities_get.get_start_activities(log, parameters=parameters).keys())
    end_activities = list(end_activities_get.get_end_activities(log, parameters=parameters).keys())
    contains_empty_traces = False
    traces_length = [len(trace) for trace in log]
    if traces_length:
        contains_empty_traces = min([len(trace) for trace in log]) == 0

    # set the threshold parameter based on f and the max value in the dfg:
    max_value = 0
    for key, value in dfg:
        if value > max_value:
            max_value = value
    threshold = noise_threshold * max_value

    recursion_depth = 0
    sub = subtree.make_tree(log, dfg, dfg, dfg, activities, c, recursion_depth, noise_threshold, threshold,
                            start_activities, end_activities,
                            start_activities, end_activities, parameters=parameters)

    process_tree = get_tree_repr_implain.get_repr(sub, 0, contains_empty_traces=contains_empty_traces)
    # Ensures consistency to the parent pointers in the process tree
    tree_consistency.fix_parent_pointers(process_tree)
    # Fixes a 1 child XOR that is added when single-activities flowers are found
    tree_consistency.fix_one_child_xor_flower(process_tree)
    # folds the process tree (to simplify it in case fallthroughs/filtering is applied)
    process_tree = generic.fold(process_tree)
    # sorts the process tree to ensure consistency in different executions of the algorithm
    tree_sort(process_tree)

    return process_tree


def apply_tree_variants(variants, parameters=None):
    """
    Apply the IM_F algorithm to a dictionary of variants obtaining a process tree

    Parameters
    ----------
    variants
        Variants
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> attribute of the log to use as activity name
            (default concept:name)

    Returns
    ----------
    process_tree
        Process tree
    """
    log = EventLog()
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    var_keys = list(variants.keys())
    for var in var_keys:
        val = variants[var]
        if type(val) is list:
            val = len(val)
        for i in range(val):
            trace = variants_util.variant_to_trace(var, parameters=parameters)
            log.append(trace)

    return apply_tree(log, parameters=parameters)


def apply_infrequent_petrinet(tree):
    return tree_to_petri.apply(tree)
