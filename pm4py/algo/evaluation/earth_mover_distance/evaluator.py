import warnings
from enum import Enum

import deprecation

from pm4py.algo.evaluation.earth_mover_distance.variants import pyemd
from pm4py.util import exec_utils


class Variants(Enum):
    PYEMD = pyemd


DEFAULT_VARIANT = Variants.PYEMD


@deprecation.deprecated('2.2.5', '2.4.0', details='use algorithm.py entrypoint')
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
    warnings.warn('use algorithm.py entrypoint', DeprecationWarning)
    return exec_utils.get_variant(variant).apply(lang1, lang2, parameters=parameters)
