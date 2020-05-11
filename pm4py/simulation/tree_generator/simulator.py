from pm4py.simulation.tree_generator.versions import basic, ptandloggenerator
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    BASIC = basic
    PTANDLOGGENERATOR = ptandloggenerator


BASIC = Variants.BASIC
PTANDLOGGENERATOR = Variants.PTANDLOGGENERATOR
DEFAULT_VARIANT = Variants.PTANDLOGGENERATOR

VERSIONS = {Variants.BASIC, Variants.PTANDLOGGENERATOR}


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
    return exec_utils.get_variant(variant).apply(parameters=parameters)
