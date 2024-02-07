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
from pm4py.objects.conversion.process_tree.variants import to_petri_net
from pm4py.objects.conversion.process_tree.variants import to_petri_net_transition_bordered
from pm4py.objects.conversion.process_tree.variants import to_bpmn
from pm4py.objects.conversion.process_tree.variants import to_powl
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    TO_PETRI_NET = to_petri_net
    TO_PETRI_NET_TRANSITION_BORDERED = to_petri_net_transition_bordered
    TO_BPMN = to_bpmn
    TO_POWL = to_powl


def apply(tree, parameters=None, variant=Variants.TO_PETRI_NET):
    """
    Method for converting from Process Tree to Petri net

    Parameters
    -----------
    tree
        Process tree
    parameters
        Parameters of the algorithm
    variant
        Chosen variant of the algorithm:
            - Variants.TO_PETRI_NET
            - Variants.TO_PETRI_NET_TRANSITION_BORDERED

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    return exec_utils.get_variant(variant).apply(tree, parameters=parameters)
