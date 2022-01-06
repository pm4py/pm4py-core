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
from pm4py.objects.process_tree.obj import ProcessTree
from typing import Optional, Dict, Any, Union
from pm4py.util import typing, exec_utils
from enum import Enum
from collections import Counter
from pm4py.objects.process_tree.utils import bottomup


class Parameters(Enum):
    NUM_EVENTS_PROPERTY = "num_events_property"
    NUM_CASES_PROPERTY = "num_cases_property"


def apply(pt: ProcessTree, align_result: Union[typing.AlignmentResult, typing.ListAlignments],
          parameters: Optional[Dict[Any, Any]] = None) -> ProcessTree:
    """
    Annotate a process tree with frequency information (number of events / number of cases),
    given the results of an alignment performed on the process tree.

    Parameters
    ----------------
    pt
        Process tree
    parameters
        Parameters of the algorithm, including:
        - Parameters.NUM_EVENTS_PROPERTY => number of events
        - Parameters.NUM_CASES_PROPERTY => number of cases

    Returns
    ----------------
    pt
        Annotated process tree
    """
    if parameters is None:
        parameters = {}

    num_events_property = exec_utils.get_param_value(Parameters.NUM_EVENTS_PROPERTY, parameters, "num_events")
    num_cases_property = exec_utils.get_param_value(Parameters.NUM_CASES_PROPERTY, parameters, "num_cases")
    bottomup_nodes = bottomup.get_bottomup_nodes(pt, parameters=parameters)

    all_paths_open_enabled_events = []
    all_paths_open_enabled_cases = []
    for trace in align_result:
        state = trace["state"]
        paths = []
        while state.parent is not None:
            if state.path:
                paths.append(state.path)
            state = state.parent
        paths.reverse()
        paths_enabled = [y[0] for x in paths for y in x if y[1] is ProcessTree.OperatorState.ENABLED]
        paths_open = [y[0] for x in paths for y in x if y[1] is ProcessTree.OperatorState.OPEN if
                      y[0] not in paths_enabled]
        all_paths_open_enabled_events = all_paths_open_enabled_events + paths_enabled + paths_open
        all_paths_open_enabled_cases = all_paths_open_enabled_cases + list(set(paths_enabled + paths_open))
    all_paths_open_enabled_events_counter = Counter(all_paths_open_enabled_events)
    all_paths_open_enabled_cases_counter = Counter(all_paths_open_enabled_cases)

    for node in bottomup_nodes:
        node._properties[num_events_property] = all_paths_open_enabled_events_counter[node]
        node._properties[num_cases_property] = all_paths_open_enabled_cases_counter[node]

    return pt
