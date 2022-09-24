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
from pm4py.algo.discovery.footprints.tree.variants import bottomup as bottomup_discovery
from pm4py.objects.process_tree.utils import bottomup as bottomup_util
from enum import Enum

class Outputs(Enum):
    DFG = "dfg"
    SEQUENCE = "sequence"
    PARALLEL = "parallel"
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"
    ACTIVITIES = "activities"
    SKIPPABLE = "skippable"
    ACTIVITIES_ALWAYS_HAPPENING = "activities_always_happening"
    MIN_TRACE_LENGTH = "min_trace_length"
    TRACE = "trace"


FP_DEV_COLOR = "red"
FP_START_END_DEV_COLOR = "blue"
FP_ALWAYS_EXECUTED_DEV_COLOR = "orange"

FOOTPRINTS_KEY = "footprints"
START_ACTIVITIES = "start_activities"
END_ACTIVITIES = "end_activities"
ALWAYS_EXECUTED = "always_executed"


def apply(tree, conf_results, parameters=None):
    """
    Projects conformance results on top of the process tree

    Parameters
    --------------
    tree
        Process tree
    conf_results
        Conformance results (footprints on the entire log vs entire model)
    parameters
        Parameters of the algorithm

    Returns
    --------------
    color_map
        Color map to be provided to the visualization
    """
    if parameters is None:
        parameters = {}

    start_activities = {}
    end_activities = {}

    if isinstance(conf_results, list):
        raise Exception("the visualization can only be applied with total footprints (not trace-by-trace)!")
    elif isinstance(conf_results, dict):
        footprints = conf_results
        start_activities = conf_results[START_ACTIVITIES]
        end_activities = conf_results[END_ACTIVITIES]
    else:
        footprints = conf_results

    bottomup_nodes = bottomup_util.get_bottomup_nodes(tree, parameters=parameters)
    labels_dictio = {x.label: x for x in bottomup_nodes if x.operator is None and x.label is not None}
    all_fp_dictio = bottomup_discovery.get_all_footprints(tree, parameters=parameters)
    conf_colors = {}

    for res in start_activities:
        if res in labels_dictio:
            conf_colors[labels_dictio[res]] = FP_START_END_DEV_COLOR

    for res in end_activities:
        if res in labels_dictio:
            conf_colors[labels_dictio[res]] = FP_START_END_DEV_COLOR

    for res in footprints:
        if res[0] in labels_dictio and res[1] in labels_dictio:
            conf_colors[labels_dictio[res[0]]] = FP_DEV_COLOR
            conf_colors[labels_dictio[res[1]]] = FP_DEV_COLOR
            for n in bottomup_nodes:
                if res[0] in all_fp_dictio[n][Outputs.ACTIVITIES.value] and res[1] in all_fp_dictio[n][
                    Outputs.ACTIVITIES.value]:
                    conf_colors[n] = FP_DEV_COLOR
                    break

    return conf_colors
