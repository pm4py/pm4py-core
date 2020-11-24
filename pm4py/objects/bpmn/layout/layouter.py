from enum import Enum

from pm4py.objects.bpmn.layout.variants import pygraphviz
from pm4py.util import exec_utils


class Variants(Enum):
    PYGRAPHVIZ = pygraphviz


DEFAULT_VARIANT = Variants.PYGRAPHVIZ


def apply(bpmn_graph, variant=DEFAULT_VARIANT, parameters=None):
    """
    Layouts a BPMN graph (inserting the positions of the nodes and the layouting of the edges)

    Parameters
    -------------
    bpmn_graph
        BPMN graph
    variant
        Variant of the algorithm to use, possible values:
        - Variants.PYGRAPHVIZ
    parameters
        Parameters of the algorithm

    Returns
    -------------
    bpmn_graph
        BPMN graph with layout information
    """
    return exec_utils.get_variant(variant).apply(bpmn_graph, parameters=parameters)
