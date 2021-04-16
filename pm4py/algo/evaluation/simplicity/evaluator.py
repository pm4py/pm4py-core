from pm4py.algo.evaluation.simplicity.variants import arc_degree
from enum import Enum
from pm4py.util import exec_utils
import deprecation


class Variants(Enum):
    SIMPLICITY_ARC_DEGREE = arc_degree


SIMPLICITY_ARC_DEGREE = Variants.SIMPLICITY_ARC_DEGREE

VERSIONS = {SIMPLICITY_ARC_DEGREE}


@deprecation.deprecated('2.2.5', '3.0.0', details='please use pm4py.algo.evaluation.simplicity.algorithm instead')
def apply(petri_net, parameters=None, variant=SIMPLICITY_ARC_DEGREE):
    return exec_utils.get_variant(variant).apply(petri_net, parameters=parameters)
