from enum import Enum
from pm4py.algo.conformance.footprints.variants import log_model, log_extensive, trace_extensive
from pm4py.util import exec_utils


class Variants(Enum):
    LOG_MODEL = log_model
    LOG_EXTENSIVE = log_extensive
    TRACE_EXTENSIVE = trace_extensive


def apply(log_footprints, model_footprints, variant=Variants.LOG_MODEL, parameters=None):
    """
    Apply footprints conformance between a log footprints object
    and a model footprints object

    Parameters
    -----------------
    log_footprints
        Footprints of the log
    model_footprints
        Footprints of the model
    parameters
        Parameters of the algorithm, including:
            - Parameters.STRICT => strict check of the footprints

    Returns
    ------------------
    violations
        Set/dictionary of all the violations between the log footprints
        and the model footprints, OR list of case-per-case violations
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(log_footprints, model_footprints, parameters=parameters)
