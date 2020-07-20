from pm4py.objects.process_tree.exporter.variants import ptml
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    PTML = ptml


DEFAULT_VARIANT = Variants.PTML


def apply(tree, output_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Exports the process tree to a file

    Parameters
    ----------------
    tree
        Process tree
    output_path
        Output path
    variant
        Variant of the algorithm:
            - Variants.PTML
    parameters
        Parameters
    """
    return exec_utils.get_variant(variant).apply(tree, output_path, parameters=parameters)
