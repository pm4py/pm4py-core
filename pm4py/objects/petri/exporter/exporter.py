from pm4py.objects.petri.exporter.versions import pnml
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    PNML = pnml


PNML = Variants.PNML


def apply(net, initial_marking, output_filename, final_marking=None, variant=PNML, parameters=None):
    """
    Export a Petri net along with an initial marking (and possibly a final marking) to an output file

    Parameters
    ------------
    net
        Petri net
    initial_marking
        Initial marking
    output_filename
        Output filename
    final_marking
        Final marking
    variant
        Variant of the algorithm, possible values:
            - Variants.PNML
    parameters
        Parameters of the exporter
    """
    return exec_utils.get_variant(variant).export_net(net, initial_marking, output_filename, final_marking=final_marking, parameters=parameters)
