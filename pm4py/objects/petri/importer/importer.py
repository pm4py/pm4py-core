from pm4py.objects.petri.importer.versions import pnml
from pm4py.util import exec_utils
from enum import Enum


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
