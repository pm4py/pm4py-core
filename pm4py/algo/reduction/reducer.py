from enum import Enum
from typing import Any

from pm4py.algo.reduction.variants import tree_tr_based
from pm4py.util import exec_utils


class Variants(Enum):
    TREE_TR_BASED = tree_tr_based


def apply(*args, **kwargs) -> Any:
    """
    Apply a reduction algorithm to a PM4Py object

    Parameters
    ---------------
    args
        Arguments of the reduction algorithm
    kwargs
        Keyword arguments of the reduction algorithm (including the variant, that is an item of the Variants enum)

    Returns
    ---------------
    reduced_obj
        Reduced object
    """
    variant = kwargs["variant"] if "variant" in kwargs else None
    if variant is None:
        raise Exception("please specify the variant of the reduction to be used.")
    return exec_utils.get_variant(variant).apply(*args, **kwargs)
