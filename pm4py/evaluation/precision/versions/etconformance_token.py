from pm4py import util as pmutil
from pm4py.algo.conformance.tokenreplay import factory as token_replay
from pm4py.objects import log as log_lib
from pm4py.evaluation.precision import utils as precision_utils
from pm4py.statistics.start_activities.log.get import get_start_activities
from pm4py.objects.petri.align_utils import get_visible_transitions_eventually_enabled_by_marking


"""
Implementation of the approach described in paper

Muñoz-Gama, Jorge, and Josep Carmona. "A fresh look at precision in process conformance." International Conference
on Business Process Management. Springer, Berlin, Heidelberg, 2010.

for measuring precision.

For each prefix in the log, the reflected tasks are calculated (outgoing attributes from the prefix)
Then, a token replay is done on the prefix in order to get activated transitions
Escaping edges is the set difference between activated transitions and reflected tasks

Then, precision is calculated by the formula used in the paper

At the moment, the precision value is different from the one provided by the ProM plug-in,
although the implementation seems to follow the paper concept
"""

PARAM_ACTIVITY_KEY = pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY

PARAMETERS = [PARAM_ACTIVITY_KEY]


def apply(log, net, marking, final_marking, parameters=None):
    """
    Get ET Conformance precision

    Parameters
    ----------
    log
        Trace log
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm, including:
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Activity key
    """

    if parameters is None:
        parameters = {}

    cleaning_token_flood = parameters["cleaning_token_flood"] if "cleaning_token_flood" in parameters else False

    activity_key = parameters[
        PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY
    # default value for precision, when no activated transitions (not even by looking at the initial marking) are found
    precision = 1.0
    sum_ee = 0
    sum_at = 0

    parameters_tr = {
        "consider_remaining_in_fitness": False,
        "try_to_reach_final_marking_through_hidden": False,
        "stop_immediately_unfit": True,
        "walk_through_hidden_trans": True,
        "cleaning_token_flood": cleaning_token_flood,
        PARAM_ACTIVITY_KEY: activity_key
    }

    prefixes, prefix_count = precision_utils.get_log_prefixes(log, activity_key=activity_key)
    prefixes_keys = list(prefixes.keys())
    fake_log = precision_utils.form_fake_log(prefixes_keys, activity_key=activity_key)

    aligned_traces = token_replay.apply(fake_log, net, marking, final_marking, parameters=parameters_tr)

    # fix: also the empty prefix should be counted!
    start_activities = set(get_start_activities(log, parameters=parameters))
    trans_en_ini_marking = set([x.label for x in get_visible_transitions_eventually_enabled_by_marking(net, marking)])
    diff = trans_en_ini_marking.difference(start_activities)
    sum_at += len(log) * len(trans_en_ini_marking)
    sum_ee += len(log) * len(diff)
    # end fix

    for i in range(len(aligned_traces)):
        if aligned_traces[i]["trace_is_fit"]:
            log_transitions = set(prefixes[prefixes_keys[i]])
            activated_transitions_labels = set(
                [x.label for x in aligned_traces[i]["enabled_transitions_in_marking"] if x.label is not None])
            sum_at += len(activated_transitions_labels) * prefix_count[prefixes_keys[i]]
            escaping_edges = activated_transitions_labels.difference(log_transitions)
            sum_ee += len(escaping_edges) * prefix_count[prefixes_keys[i]]

    if sum_at > 0:
        precision = 1 - float(sum_ee) / float(sum_at)

    return precision
