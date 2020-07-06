from enum import Enum
from pm4py.util import exec_utils
from pm4py.algo.discovery.footprints.outputs import Outputs


class Parameters(Enum):
    STRICT = "strict"


def apply_single(log_footprints, model_footprints, parameters=None):
    """
    Apply footprints conformance between a log footprints object
    and a model footprints object

    Parameters
    -----------------
    log_footprints
        Footprints of the log (NOT a list, but a single footprints object)
    model_footprints
        Footprints of the model
    parameters
        Parameters of the algorithm, including:
            - Parameters.STRICT => strict check of the footprints

    Returns
    ------------------
    violations
        Set of all the violations between the log footprints
        and the model footprints
    """
    if parameters is None:
        parameters = {}

    strict = exec_utils.get_param_value(Parameters.STRICT, parameters, False)

    if strict:
        s1 = log_footprints[Outputs.SEQUENCE.value].difference(model_footprints[Outputs.SEQUENCE.value])
        s2 = log_footprints[Outputs.PARALLEL.value].difference(model_footprints[Outputs.PARALLEL.value])

        violations = s1.union(s2)

    else:
        s1 = log_footprints[Outputs.SEQUENCE.value].union(log_footprints[Outputs.PARALLEL.value])
        s2 = model_footprints[Outputs.SEQUENCE.value].union(model_footprints[Outputs.PARALLEL.value])

        violations = s1.difference(s2)

    return violations


def apply(log_footprints, model_footprints, parameters=None):
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
        Set of all the violations between the log footprints
        and the model footprints, OR list of case-per-case violations
    """
    if type(log_footprints) is list:
        ret = []
        for case_footprints in log_footprints:
            ret.append(apply_single(case_footprints, model_footprints, parameters=parameters))
        return ret
    return apply_single(log_footprints, model_footprints, parameters=parameters)
