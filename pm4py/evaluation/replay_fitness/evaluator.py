from pm4py.evaluation.replay_fitness.versions import alignment_based, token_replay
from pm4py.algo.conformance import alignments
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects import petri
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    ALIGNMENT_BASED = alignment_based
    TOKEN_BASED = token_replay


class Parameters(Enum):
    ALIGN_VARIANT = "align_variant"


ALIGNMENT_BASED = Variants.ALIGNMENT_BASED
TOKEN_BASED = Variants.TOKEN_BASED

VERSIONS = {ALIGNMENT_BASED, TOKEN_BASED}


def apply(log, petri_net, initial_marking, final_marking, parameters=None, variant=None):
    """
    Apply fitness evaluation starting from an event log and a marked Petri net,
    by using one of the replay techniques provided by PM4Py

    Parameters
    -----------
    log
        Trace log object
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters related to the replay algorithm
    variant
        Chosen variant:
            - Variants.ALIGNMENT_BASED
            - Variants.TOKEN_BASED

    Returns
    ----------
    fitness_eval
        Fitness evaluation
    """
    if parameters is None:
        parameters = {}

    # execute the following part of code when the variant is not specified by the user
    if variant is None:
        if not (
                petri.check_soundness.check_easy_soundness_net_in_fin_marking(petri_net, initial_marking,
                                                                              final_marking)):
            # in the case the net is not a easy sound workflow net, we must apply token-based replay
            variant = TOKEN_BASED
        else:
            # otherwise, use the align-etconformance approach (safer, in the case the model contains duplicates)
            variant = ALIGNMENT_BASED

    if variant == TOKEN_BASED:
        # execute the token-based replay variant
        return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG),
                                                     petri_net,
                                                     initial_marking, final_marking, parameters=parameters)
    else:
        # execute the alignments based variant, with the specification of the alignments variant
        align_variant = exec_utils.get_param_value(Parameters.ALIGN_VARIANT, parameters,
                                                   alignments.algorithm.DEFAULT_VARIANT)
        return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG),
                                                     petri_net,
                                                     initial_marking, final_marking, align_variant=align_variant,
                                                     parameters=parameters)


def evaluate(results, parameters=None, variant=TOKEN_BASED):
    """
    Evaluate replay results when the replay algorithm has already been applied

    Parameters
    -----------
    results
        Results of the replay algorithm
    parameters
        Possible parameters passed to the evaluation
    variant
        Indicates which evaluator is called

    Returns
    -----------
    fitness_eval
        Fitness evaluation
    """
    return exec_utils.get_variant(variant).evaluate(results, parameters=parameters)
