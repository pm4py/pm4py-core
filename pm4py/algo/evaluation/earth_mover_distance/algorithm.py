from pm4py.algo.evaluation.earth_mover_distance.variants import pyemd
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, List


class Variants(Enum):
    PYEMD = pyemd


DEFAULT_VARIANT = Variants.PYEMD


def apply(lang1: Dict[List[str], float], lang2: Dict[List[str], float], variant=Variants.PYEMD, parameters: Optional[Dict[Any, Any]] = None) -> float:
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
    return exec_utils.get_variant(variant).apply(lang1, lang2, parameters=parameters)
