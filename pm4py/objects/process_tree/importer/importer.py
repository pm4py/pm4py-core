from pm4py.objects.process_tree.importer.variants import ptml
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    PTML = ptml


DEFAULT_VARIANT = Variants.PTML


def apply(file_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Imports a process tree from the specified path

    Parameters
    ---------------
    path
        Path
    variant
        Variant of the algorithm, possible values:
            - Variants.PTML
    parameters
        Possible parameters (version specific)

    Returns
    ---------------
    tree
        Process tree
    """
    return exec_utils.get_variant(variant).apply(file_path, parameters=parameters)
