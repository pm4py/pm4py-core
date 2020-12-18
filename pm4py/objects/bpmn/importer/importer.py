from enum import Enum

from pm4py.objects.bpmn.importer.variants import lxml
from pm4py.util import exec_utils


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


def deserialize(bpmn_string, variant=DEFAULT_VARIANT, parameters=None):
    """
    Deserialize a text/binary string representing a BPMN 2.0

    Parameters
    -------------
    bpmn_string
        BPMN string
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

    return exec_utils.get_variant(variant).import_from_string(bpmn_string, parameters=parameters)
