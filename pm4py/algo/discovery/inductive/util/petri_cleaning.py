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
from pm4py.objects.petri_net.utils.petri_utils import remove_transition


def petri_reduction_treplay(net, parameters=None):
    """
    Apply petri_reduction on the Petrinet removing hidden transitions
    that are unused according to token-based replay

    Parameters
    -----------
    net
        Petri net
    parameters
        Parameters of the algorithm, including:
            aligned_traces -> Result of alignment according to token-based replay
    Returns
    -----------
    net
        Reduced Petri net
    """
    if parameters is None:
        parameters = {}

    aligned_traces = parameters["aligned_traces"]

    enabled_trans_in_at_least_one_trace = set()

    for trace in aligned_traces:
        for trans in trace["activated_transitions"]:
            enabled_trans_in_at_least_one_trace.add(trans)

    transitions = list(net.transitions)
    for trans in transitions:
        if trans.label is None:
            if trans not in enabled_trans_in_at_least_one_trace:
                net = remove_transition(net, trans)

    return net
