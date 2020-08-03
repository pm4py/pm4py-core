from pm4py.algo.discovery.footprints.outputs import Outputs
from enum import Enum


class ConfOutputs(Enum):
    FOOTPRINTS = "footprints"
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"
    MIN_LENGTH_FIT = "min_length_fit"
    IS_FOOTPRINTS_FIT = "is_footprints_fit"


def apply(log_footprints, model_footprints, parameters=None):
    """
    Apply footprints conformance between a log footprints object
    and a model footprints object

    Parameters
    -----------------
    log_footprints
        Footprints of the log (entire log)
    model_footprints
        Footprints of the model
    parameters
        Parameters of the algorithm

    Returns
    ------------------
    violations
        Dictionary containing all the violations
    """
    if parameters is None:
        parameters = {}

    if type(log_footprints) is list:
        raise Exception(
            "it is possible to apply this variant only on overall log footprints, not trace-by-trace footprints!")

    log_configurations = log_footprints[Outputs.SEQUENCE.value].union(log_footprints[Outputs.PARALLEL.value])
    model_configurations = model_footprints[Outputs.SEQUENCE.value].union(model_footprints[Outputs.PARALLEL.value])

    ret = {}
    ret[ConfOutputs.FOOTPRINTS.value] = set(x for x in log_configurations if x not in model_configurations)
    ret[ConfOutputs.START_ACTIVITIES.value] = set(x for x in log_footprints[Outputs.START_ACTIVITIES.value] if
                                                  x not in model_footprints[
                                                      Outputs.START_ACTIVITIES.value]) if Outputs.START_ACTIVITIES.value in model_footprints else set()
    ret[ConfOutputs.END_ACTIVITIES.value] = set(
        x for x in log_footprints[Outputs.END_ACTIVITIES.value] if x not in model_footprints[
            Outputs.END_ACTIVITIES.value]) if Outputs.END_ACTIVITIES.value in model_footprints else set()
    ret[ConfOutputs.MIN_LENGTH_FIT.value] = log_footprints[Outputs.MIN_TRACE_LENGTH.value] >= model_footprints[
        Outputs.MIN_TRACE_LENGTH.value] if Outputs.MIN_TRACE_LENGTH.value in log_footprints and Outputs.MIN_TRACE_LENGTH.value in model_footprints else True
    ret[ConfOutputs.IS_FOOTPRINTS_FIT.value] = len(ret[ConfOutputs.FOOTPRINTS.value]) == 0 and len(
        ret[ConfOutputs.START_ACTIVITIES.value]) == 0 and len(
        ret[ConfOutputs.END_ACTIVITIES.value]) == 0 and ret[ConfOutputs.MIN_LENGTH_FIT.value]

    return ret
