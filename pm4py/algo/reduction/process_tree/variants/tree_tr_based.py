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
from copy import deepcopy
from typing import Optional, Dict, Any, List, Set

from pm4py.objects.log.obj import Trace
from pm4py.objects.process_tree.utils import bottomup
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.process_tree.utils.generic import fold
from pm4py.util import constants, xes_constants, exec_utils
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


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(tree: ProcessTree, trace: Trace, parameters: Optional[Dict[Any, Any]] = None, **kwargs) -> ProcessTree:
    """
    Reduce a process tree replacing the skippable elements that have empty intersection with the
    trace.

    Parameters
    -----------------
    tree
        Process tree
    trace
        Trace of an event log
    parameters
        Parameters of the algorithm, possible values: Parameters.ACTIVITY_KEY

    Returns
    ------------------
    tree
        Reduced process tree
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    activities = set(x[activity_key] for x in trace)

    tree = deepcopy(tree)
    from pm4py.algo.discovery.footprints.tree.variants import bottomup as footprints

    bottomup_nodes = bottomup.get_bottomup_nodes(tree)
    fps = footprints.get_all_footprints(tree)
    fps = {id(x): y for x, y in fps.items()}

    return reduce(bottomup_nodes, fps, activities)


def reduce(bottomup_nodes: List[ProcessTree], fps: Dict[str, Any], activities: Set[str]) -> ProcessTree:
    """
    Reduce a process tree replacing the skippable elements that have empty intersection with the
    trace.

    Parameters
    -----------------
    bottomup_nodes
        List of nodes of the process tree (that are process trees by themselves) in a bottomup order
    fps
        Footprints of the process tree
    activities
        Set of activities in the trace

    Returns
    ------------------
    tree
        Reduced process tree
    """
    i = 0
    while i < len(bottomup_nodes) - 1:
        node = bottomup_nodes[i]
        parent = node.parent

        is_skippable = fps[id(node)][Outputs.SKIPPABLE.value]
        node_activities = fps[id(node)][Outputs.ACTIVITIES.value]

        if is_skippable and not node_activities.intersection(activities):
            pt = ProcessTree()
            pt.parent = parent
            parent.children[parent.children.index(node)] = pt
        i = i + 1

    return fold(bottomup_nodes[-1])
