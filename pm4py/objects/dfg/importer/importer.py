from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.dfg.importer.variants import classic


class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC


def apply(file_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Import a DFG (along with the start and end activities)

    Parameters
    --------------
    file_path
        Path of the DFG file
    variant
        Variant of the importer, possible values:
            - Variants.CLASSIC: importing from a .dfg file
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    return exec_utils.get_variant(variant).apply(file_path, parameters=parameters)
