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

from pm4py.objects.bpmn.layout.variants import graphviz
from pm4py.util import exec_utils


class Variants(Enum):
    GRAPHVIZ = graphviz


DEFAULT_VARIANT = Variants.GRAPHVIZ


def apply(bpmn_graph, variant=DEFAULT_VARIANT, parameters=None):
    """
    Layouts a BPMN graph (inserting the positions of the nodes and the layouting of the edges)

    Parameters
    -------------
    bpmn_graph
        BPMN graph
    variant
        Variant of the algorithm to use, possible values:
        - Variants.GRAPHVIZ
    parameters
        Parameters of the algorithm

    Returns
    -------------
    bpmn_graph
        BPMN graph with layout information
    """
    return exec_utils.get_variant(variant).apply(bpmn_graph, parameters=parameters)
