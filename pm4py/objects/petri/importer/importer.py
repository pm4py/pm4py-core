from enum import Enum

from pm4py.objects.petri.importer.variants import pnml
from pm4py.util import exec_utils


class Variants(Enum):
    PNML = pnml


PNML = Variants.PNML


def apply(input_file_path, variant=PNML, parameters=None):
    """
    Import a Petri net from a PNML file

    Parameters
    ------------
    input_file_path
        Input file path
    parameters
        Other parameters of the importer
    variant
        Variant of the algorithm to use, possible values:
            - Variants.PNML
    """
    return exec_utils.get_variant(variant).import_net(input_file_path, parameters=parameters)


def deserialize(petri_string, variant=PNML, parameters=None):
    """
    Deserialize a text/binary string representing a Petri net in the PNML format

    Parameters
    ----------
    petri_string
        Petri net expressed as PNML string
    variant
        Variant of the algorithm to use, possible values:
            - Variants.PNML
    parameters
        Other parameters of the algorithm
    """
    return exec_utils.get_variant(variant).import_net_from_string(petri_string, parameters=parameters)
