from enum import Enum

from pm4py.objects.dfg.exporter.variants import classic
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC


def apply(dfg, output_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Exports a DFG

    Parameters
    ---------------
    dfg
        Directly-Follows Graph
    output_path
        Output path
    variant
        Variants of the exporter, possible values:
            - Variants.CLASSIC: exporting to a .dfg file
    parameters
        Variant-specific parameters
    """
    exec_utils.get_variant(variant).apply(dfg, output_path, parameters=parameters)


def serialize(dfg, variant=DEFAULT_VARIANT, parameters=None):
    """
    Serializes a DFG object into a binary string

    Parameters
    --------------
    dfg
        DFG
    variant
        Variants of the exporter, possible values:
            - Variants.CLASSIC: exporting to a .dfg file
    parameters
        Variant-specific parameters

    Returns
    --------------
    serialization
        String that represents the DFG
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).export_as_string(dfg, parameters=parameters)
