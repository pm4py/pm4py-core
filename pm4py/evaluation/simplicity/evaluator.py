from pm4py.evaluation.simplicity.versions import arc_degree
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    SIMPLICITY_ARC_DEGREE = arc_degree


SIMPLICITY_ARC_DEGREE = Variants.SIMPLICITY_ARC_DEGREE

VERSIONS = {SIMPLICITY_ARC_DEGREE}


def apply(petri_net, parameters=None, variant=SIMPLICITY_ARC_DEGREE):
    return exec_utils.get_variant(variant).apply(petri_net, parameters=parameters)
