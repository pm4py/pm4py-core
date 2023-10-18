from pm4py.algo.simulation.playout.process_tree.variants import basic_playout
from pm4py.algo.simulation.playout.process_tree.variants import extensive, topbottom
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.process_tree.obj import ProcessTree
from typing import Optional, Dict, Any
from pm4py.objects.log.obj import EventLog


class Variants(Enum):
    BASIC_PLAYOUT = basic_playout
    EXTENSIVE = extensive
    TOPBOTTOM = topbottom


DEFAULT_VARIANT = Variants.TOPBOTTOM


def apply(tree: ProcessTree, variant=DEFAULT_VARIANT, parameters: Optional[Dict[Any, Any]] = None) -> EventLog:
    """
    Performs a playout of a process tree

    Parameters
    ---------------
    tree
        Process tree
    variant
        Variant of the algorithm:
        - Variants.BASIC_PLAYOUT: basic playout
        - Variants.EXTENSIVE: extensive playout (all the possible traces)
    parameters
        Parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(tree, parameters=parameters)
