from pm4py.util import exec_utils
from pm4py.objects.dfg.exporter.variants import classic
from enum import Enum


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
