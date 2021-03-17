from pm4py.evaluation.simplicity.variants import arc_degree
from enum import Enum
from pm4py.util import exec_utils
import deprecation
from pm4py.meta import VERSION
import warnings


class Variants(Enum):
    SIMPLICITY_ARC_DEGREE = arc_degree


SIMPLICITY_ARC_DEGREE = Variants.SIMPLICITY_ARC_DEGREE

VERSIONS = {SIMPLICITY_ARC_DEGREE}


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0",
                        current_version=VERSION,
                        details="Use the pm4py.algo.evaluation.simplicity package")
def apply(petri_net, parameters=None, variant=SIMPLICITY_ARC_DEGREE):
    warnings.warn("Use the pm4py.algo.evaluation.simplicity package")
    return exec_utils.get_variant(variant).apply(petri_net, parameters=parameters)
