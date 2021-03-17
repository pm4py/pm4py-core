import warnings
from typing import List, Dict, Any, Union

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


def __convert_to_fp(*args) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Internal method to convert the provided event log / process model argument
    to footprints (using footprints discovery)

    Parameters
    ----------------
    args
        Event log / process model

    Returns
    ---------------
    fp
        Footprints
    """
    import pm4py
    while type(args) is tuple:
        if len(args) == 1:
            args = args[0]
        else:
            fp = pm4py.discover_footprints(*args)
            return fp
    if type(args) is list or type(args) is dict:
        return args
    fp = pm4py.discover_footprints(args)
    return fp


def conformance_diagnostics_footprints(*args) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Provide conformance checking diagnostics using footprints

    Parameters
    ----------------
    args
        Provided argument:
        - The first argument is supposed to be an event log (or the footprints discovered from the event log)
        - The other arguments are supposed to be the process model (or the footprints discovered from the process model)

    Returns
    ----------------
    fps
        Footprints of the event log / process model
    """
    fp1 = __convert_to_fp(args[0])
    fp2 = __convert_to_fp(args[1:])
    from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
    if isinstance(fp1, list):
        return footprints_conformance.apply(fp1, fp2, variant=footprints_conformance.Variants.TRACE_EXTENSIVE)
    else:
        return footprints_conformance.apply(fp1, fp2, variant=footprints_conformance.Variants.LOG_EXTENSIVE)


def fitness_footprints(*args) -> Dict[str, float]:
    """
    Calculates fitness using footprints

    Parameters
    ----------------
    args
        Provided argument:
        - The first argument is supposed to be an event log (or the footprints discovered from the event log)
        - The other arguments are supposed to be the process model (or the footprints discovered from the process model)

    Returns
    ----------------
    fitness_dict
        A dictionary containing two keys:
        - perc_fit_traces => percentage of fit traces (over the log)
        - log_fitness => the fitness value over the log
    """
    fp_conf = conformance_diagnostics_footprints(*args)
    fp1 = __convert_to_fp(args[0])
    fp2 = __convert_to_fp(args[1:])
    from pm4py.algo.conformance.footprints.util import evaluation
    return evaluation.fp_fitness(fp1, fp2, fp_conf)


def precision_footprints(*args) -> float:
    """
    Calculates precision using footprints

    Parameters
    ----------------
    args
        Provided argument:
        - The first argument is supposed to be an event log (or the footprints discovered from the event log)
        - The other arguments are supposed to be the process model (or the footprints discovered from the process model)

    Returns
    ----------------
    precision
        The precision of the process model (as a number between 0 and 1)
    """
    fp1 = __convert_to_fp(args[0])
    fp2 = __convert_to_fp(args[1:])
    from pm4py.algo.conformance.footprints.util import evaluation
    return evaluation.fp_precision(fp1, fp2)
