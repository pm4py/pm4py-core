from pm4py.simulation.tree_playout.variants import basic_playout, extensive, topbottom
from enum import Enum
from pm4py.util import exec_utils
import deprecation
from pm4py.meta import VERSION
import warnings


class Variants(Enum):
    BASIC_PLAYOUT = basic_playout
    EXTENSIVE = extensive
    TOPBOTTOM = topbottom


DEFAULT_VARIANT = Variants.TOPBOTTOM


@deprecation.deprecated(deprecated_in="2.2.5", removed_in="3.0",
                        current_version=VERSION,
                        details="Use the pm4py.algo.simulation.tree_playout package")
def apply(tree, variant=DEFAULT_VARIANT, parameters=None):
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
    warnings.warn("Use the pm4py.algo.simulation.tree_playout package")
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(tree, parameters=parameters)
