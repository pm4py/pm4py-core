from enum import Enum

from pm4py.objects.petri.exporter.variants import pnml
from pm4py.util import exec_utils


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
    return exec_utils.get_variant(variant).export_net(net, initial_marking, output_filename,
                                                      final_marking=final_marking, parameters=parameters)


def serialize(net, initial_marking, final_marking=None, variant=PNML):
    """
    Serialize a Petri net along with an initial marking (and possibly a final marking) to a binary PNML string

    Parameters
    ------------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    variant
        Variant of the algorithm, possible values:
            - Variants.PNML

    Returns
    -------------
    serialization
        Binary string (BPMN 2.0 XML standard)
    """
    return exec_utils.get_variant(variant).export_petri_as_string(net, initial_marking, final_marking=final_marking)
