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
from pm4py.objects.process_tree import semantics
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.process_tree.obj import ProcessTree


class Parameters:
    NO_TRACES = "num_traces"


def apply(tree: ProcessTree, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Generate a log by a playout operation

    Parameters
    ---------------
    tree
        Process tree
    parameters
        Parameters of the algorithm, including:
        - Parameters.NO_TRACES: number of traces of the playout

    Returns
    --------------
    log
        Simulated log
    """
    if parameters is None:
        parameters = {}

    no_traces = exec_utils.get_param_value(Parameters.NO_TRACES, parameters, 1000)

    log = semantics.generate_log(tree, no_traces=no_traces)

    return log
