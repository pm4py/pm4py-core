from pm4py.simulation.tree_generator.variants import basic, ptandloggenerator
from enum import Enum
from pm4py.util import exec_utils
import deprecation
from pm4py.meta import VERSION
import warnings


class Variants(Enum):
    BASIC = basic
    PTANDLOGGENERATOR = ptandloggenerator


BASIC = Variants.BASIC
PTANDLOGGENERATOR = Variants.PTANDLOGGENERATOR
DEFAULT_VARIANT = Variants.PTANDLOGGENERATOR

VERSIONS = {Variants.BASIC, Variants.PTANDLOGGENERATOR}


@deprecation.deprecated(deprecated_in="2.2.5", removed_in="3.0",
                        current_version=VERSION,
                        details="Use the pm4py.algo.simulation.tree_generator package")
def apply(variant=DEFAULT_VARIANT, parameters=None):
    """
    Generate a process tree

    Parameters
    ------------
    variant
        Variant of the algorithm. Admitted values:
            - Variants.BASIC
            - Variants.PTANDLOGGENERATOR
    parameters
        Specific parameters of the algorithm

    Returns
    ------------
    tree
        Process tree
    """
    warnings.warn("Use the pm4py.algo.simulation.tree_generator package")
    return exec_utils.get_variant(variant).apply(parameters=parameters)
