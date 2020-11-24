from pm4py.util import exec_utils
from enum import Enum
from pm4py.objects.bpmn.importer.variants import lxml


class Variants(Enum):
    LXML = lxml


DEFAULT_VARIANT = Variants.LXML


def apply(path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Imports a BPMN diagram from a file

    Parameters
    -------------
    path
        Path to the file
    variant
        Variant of the algorithm to use, possible values:
        - Variants.LXML
    parameters
        Parameters of the algorithm

    Returns
    -------------
    bpmn_graph
        BPMN graph
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(path, parameters=parameters)
