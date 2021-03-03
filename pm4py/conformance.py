import warnings
from typing import List, Dict, Any

from deprecation import deprecated

from pm4py.objects.log.log import EventLog
from pm4py.objects.petri.petrinet import PetriNet, Marking


@deprecated(deprecated_in='2.2.2', removed_in='2.3.0',
            details='conformance_tbr is deprecated, use conformance_diagnostics_token_based_replay')
def conformance_tbr(log: EventLog, petri_net: PetriNet, initial_marking: Marking,
                    final_marking: Marking) -> List[Dict[str, Any]]:
    warnings.warn('conformance_tbr is deprecated, use conformance_token_based_replay', DeprecationWarning)
    """
    Apply token-based replay for conformance checking analysis.


    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    --------------
    replay_results
        A list of replay results for each trace of the log
    """
    from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
    return token_replay.apply(log, petri_net, initial_marking, final_marking)


def conformance_diagnostics_token_based_replay(log: EventLog, petri_net: PetriNet, initial_marking: Marking,
                                               final_marking: Marking) -> List[Dict[str, Any]]:
    """
    Apply token-based replay for conformance checking analysis.
    The methods return the full token-based-replay diagnostics.

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    --------------
    replay_results
        A list of replay results for each trace of the log (in the same order as the traces in the event log)
    """
    from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
    return token_replay.apply(log, petri_net, initial_marking, final_marking)


def conformance_diagnostics_alignments(log: EventLog, petri_net: PetriNet, initial_marking: Marking,
                                       final_marking: Marking) -> List[Dict[str, Any]]:
    """
    Apply the alignments algorithm between a log and a Petri net
    The methods return the full alignment diagnostics.

    Parameters
    -------------
    log
        Event log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    -------------
    aligned_traces
        A list of alignments for each trace of the log (in the same order as the traces in the event log)
    """
    from pm4py.algo.conformance.alignments import algorithm as alignments
    return alignments.apply(log, petri_net, initial_marking, final_marking)


@deprecated(deprecated_in='2.2.2', removed_in='2.3.0',
            details='conformance_alignments is deprecated, use conformance_diagnostics_alignments')
def conformance_alignments(log: EventLog, petri_net: PetriNet, initial_marking: Marking,
                           final_marking: Marking) -> List[Dict[str, Any]]:
    warnings.warn('conformance_alignments is deprecated, use conformance_diagnostics_alignments', DeprecationWarning)
    """
    Apply the alignments algorithm between a log and a Petri net
    The methods return the full alignment diagnostics.

    Parameters
    -------------
    log
        Event log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    -------------
    aligned_traces
        A list of alignments for each trace of the log
    """
    from pm4py.algo.conformance.alignments import algorithm as alignments
    return alignments.apply(log, petri_net, initial_marking, final_marking)


def fitness_token_based_replay(log: EventLog, petri_net: PetriNet, initial_marking: Marking, final_marking: Marking) -> \
        Dict[
            str, float]:
    """
    Calculates the fitness using token-based replay.
    The fitness is calculated on a log-based level.


    Parameters
    ---------------
    log
        Event log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    ---------------
    fitness_dictionary
        dictionary describing average fitness (key: average_trace_fitness) and the percentage of fitting traces (key: percentage_of_fitting_traces)
    """
    from pm4py.evaluation.replay_fitness import evaluator as replay_fitness
    return replay_fitness.apply(log, petri_net, initial_marking, final_marking,
                                variant=replay_fitness.Variants.TOKEN_BASED)


@deprecated(deprecated_in='2.2.2', removed_in='2.3.0',
            details='evaluate_fitness_tbr is deprecated, use fitness_token_based_replay')
def evaluate_fitness_tbr(log: EventLog, petri_net: PetriNet, initial_marking: Marking, final_marking: Marking) -> Dict[
    str, float]:
    warnings.warn('evaluate_fitness_tbr is deprecated, use fitness_token_based_replay', DeprecationWarning)
    """
    Calculates the fitness using token-based replay.


    Parameters
    ---------------
    log
        Event log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    ---------------
    fitness_dictionary
        Fitness dictionary (from TBR)
    """
    from pm4py.evaluation.replay_fitness import evaluator as replay_fitness
    return replay_fitness.apply(log, petri_net, initial_marking, final_marking,
                                variant=replay_fitness.Variants.TOKEN_BASED)


def fitness_alignments(log: EventLog, petri_net: PetriNet, initial_marking: Marking, final_marking: Marking) -> \
        Dict[str, float]:
    """
    Calculates the fitness using alignments

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net object
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    ---------------
    fitness_dictionary
        dictionary describing average fitness (key: average_trace_fitness) and the percentage of fitting traces (key: percentage_of_fitting_traces)
    """
    from pm4py.evaluation.replay_fitness import evaluator as replay_fitness
    return replay_fitness.apply(log, petri_net, initial_marking, final_marking,
                                variant=replay_fitness.Variants.ALIGNMENT_BASED)


@deprecated(deprecated_in='2.2.2', removed_in='2.3.0',
            details='evaluate_fitness_alignments is deprecated, use fitness_alignments')
def evaluate_fitness_alignments(log: EventLog, petri_net: PetriNet, initial_marking: Marking, final_marking: Marking) -> \
        Dict[str, float]:
    warnings.warn('evaluate_fitness_alignments is deprecated, use fitness_alignments', DeprecationWarning)
    """
    Calculates the fitness using alignments

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net object
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    ---------------
    fitness_dictionary
        Fitness dictionary (from alignments)
    """
    from pm4py.evaluation.replay_fitness import evaluator as replay_fitness
    return replay_fitness.apply(log, petri_net, initial_marking, final_marking,
                                variant=replay_fitness.Variants.ALIGNMENT_BASED)


def precision_token_based_replay(log: EventLog, petri_net: PetriNet, initial_marking: Marking,
                                 final_marking: Marking) -> float:
    """
    Calculates the precision precision using token-based replay

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net object
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    --------------
    precision
        float representing the precision value
    """
    from pm4py.evaluation.precision import evaluator as precision_evaluator
    return precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)


@deprecated(deprecated_in='2.2.2', removed_in='2.3.0',
            details='evaluate_precision_tbr is deprecated, use precision_token_based_replay')
def evaluate_precision_tbr(log: EventLog, petri_net: PetriNet, initial_marking: Marking,
                           final_marking: Marking) -> float:
    warnings.warn('evaluate_precision_tbr is deprecated, use precision_token_based_replay', DeprecationWarning)
    """
    Calculates the precision using token-based replay

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net object
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    --------------
    precision
        float representing the precision value
    """
    from pm4py.evaluation.precision import evaluator as precision_evaluator
    return precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)


def precision_alignments(log: EventLog, petri_net: PetriNet, initial_marking: Marking,
                         final_marking: Marking) -> float:
    """
    Calculates the precision of the model w.r.t. the event log using alignments

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net object
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    --------------
    precision
        float representing the precision value
    """
    from pm4py.evaluation.precision import evaluator as precision_evaluator
    return precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE)


@deprecated(deprecated_in='2.2.2', removed_in='2.3.0',
            details='evaluate_precision_alignments is deprecated, use precision_alignments')
def evaluate_precision_alignments(log: EventLog, petri_net: PetriNet, initial_marking: Marking,
                                  final_marking: Marking) -> float:
    warnings.warn('evaluate_precision_alignments is deprecated, use precision_alignments', DeprecationWarning)
    """
    Calculates the precision using alignments

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net object
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    --------------
    precision
        float representing the precision value
    """
    from pm4py.evaluation.precision import evaluator as precision_evaluator
    return precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE)
