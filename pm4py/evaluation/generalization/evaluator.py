from pm4py.evaluation.generalization.variants import token_based
from pm4py.objects.conversion.log import converter as log_conversion
from enum import Enum
from pm4py.util import exec_utils
import deprecation
from pm4py.meta import VERSION
import warnings

class Variants(Enum):
    GENERALIZATION_TOKEN = token_based


GENERALIZATION_TOKEN = Variants.GENERALIZATION_TOKEN
VERSIONS = {GENERALIZATION_TOKEN}


@deprecation.deprecated(deprecated_in="2.2.5", removed_in="3.0",
                        current_version=VERSION,
                        details="Use the pm4py.algo.evaluation.generalization package")
def apply(log, petri_net, initial_marking, final_marking, parameters=None, variant=GENERALIZATION_TOKEN):
    warnings.warn("Use the pm4py.algo.evaluation.generalization package")
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG),
                                                 petri_net,
                                                 initial_marking, final_marking, parameters=parameters)
