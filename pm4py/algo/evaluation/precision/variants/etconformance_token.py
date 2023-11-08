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
from pm4py.algo.conformance.tokenreplay.variants import token_replay
from pm4py.algo.conformance.tokenreplay import algorithm as executor

from pm4py.objects import log as log_lib
from pm4py.algo.evaluation.precision import utils as precision_utils
from pm4py.statistics.start_activities.log.get import get_start_activities
from pm4py.objects.petri_net.utils.align_utils import get_visible_transitions_eventually_enabled_by_marking
from pm4py.util import exec_utils
from enum import Enum
from pm4py.util import constants
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.conversion.log import converter as log_converter
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    TOKEN_REPLAY_VARIANT = "token_replay_variant"
    CLEANING_TOKEN_FLOOD = "cleaning_token_flood"
    SHOW_PROGRESS_BAR = "show_progress_bar"
    MULTIPROCESSING = "multiprocessing"
    CORES = "cores"

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


def apply(log: EventLog, net: PetriNet, marking: Marking, final_marking: Marking, parameters: Optional[Dict[Union[str, Parameters], Any]] = None):
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
            Parameters.ACTIVITY_KEY -> Activity key
    """

    if parameters is None:
        parameters = {}

    cleaning_token_flood = exec_utils.get_param_value(Parameters.CLEANING_TOKEN_FLOOD, parameters, False)
    token_replay_variant = exec_utils.get_param_value(Parameters.TOKEN_REPLAY_VARIANT, parameters,
                                                      executor.Variants.TOKEN_REPLAY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, log_lib.util.xes.DEFAULT_NAME_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    show_progress_bar = exec_utils.get_param_value(Parameters.SHOW_PROGRESS_BAR, parameters, constants.SHOW_PROGRESS_BAR)

    # default value for precision, when no activated transitions (not even by looking at the initial marking) are found
    precision = 1.0
    sum_ee = 0
    sum_at = 0

    parameters_tr = {
        token_replay.Parameters.SHOW_PROGRESS_BAR: show_progress_bar,
        token_replay.Parameters.CONSIDER_REMAINING_IN_FITNESS: False,
        token_replay.Parameters.TRY_TO_REACH_FINAL_MARKING_THROUGH_HIDDEN: False,
        token_replay.Parameters.STOP_IMMEDIATELY_UNFIT: True,
        token_replay.Parameters.WALK_THROUGH_HIDDEN_TRANS: True,
        token_replay.Parameters.CLEANING_TOKEN_FLOOD: cleaning_token_flood,
        token_replay.Parameters.ACTIVITY_KEY: activity_key
    }

    if type(log) is not pd.DataFrame:
        log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    prefixes, prefix_count = precision_utils.get_log_prefixes(log, activity_key=activity_key, case_id_key=case_id_key)
    prefixes_keys = list(prefixes.keys())
    fake_log = precision_utils.form_fake_log(prefixes_keys, activity_key=activity_key)

    aligned_traces = executor.apply(fake_log, net, marking, final_marking, variant=token_replay_variant,
                                        parameters=parameters_tr)

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
