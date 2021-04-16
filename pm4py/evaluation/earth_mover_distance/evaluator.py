from pm4py.evaluation.earth_mover_distance.variants import pyemd
from enum import Enum
from pm4py.util import exec_utils
import deprecation
from pm4py.meta import VERSION
import warnings


class Variants(Enum):
    PYEMD = pyemd


DEFAULT_VARIANT = Variants.PYEMD


@deprecation.deprecated(deprecated_in="2.2.5", removed_in="3.0",
                        current_version=VERSION,
                        details="Use the pm4py.algo.evaluation.earth_mover_distance package")
def apply(lang1, lang2, variant=Variants.PYEMD, parameters=None):
    """
    Gets the EMD language between the two languages

    Parameters
    -------------
    lang1
        First language
    lang2
        Second language
    variant
        Variants of the algorithm
    parameters
        Parameters
    variants
        Variants of the algorithm, including:
            - Variants.PYEMD: pyemd based distance

    Returns
    -------------
    dist
        EMD distance
    """
    warnings.warn("Use the pm4py.algo.evaluation.earth_mover_distance package")
    return exec_utils.get_variant(variant).apply(lang1, lang2, parameters=parameters)
