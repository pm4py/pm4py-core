'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import warnings
from typing import List, Dict, Any, Union

import deprecation

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.objects.petri_net.obj import PetriNet, Marking
from collections import Counter
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util import xes_constants
from pm4py.utils import get_properties


@deprecation.deprecated(deprecated_in='2.2.2', removed_in='2.4.0',
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
    return token_replay.apply(log, petri_net, initial_marking, final_marking, parameters=get_properties(log))


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
    return token_replay.apply(log, petri_net, initial_marking, final_marking, parameters=get_properties(log))


def conformance_diagnostics_alignments(log: EventLog, *args, multi_processing: bool = False) -> List[Dict[str, Any]]:
    """
    Apply the alignments algorithm between a log and a process model.
    The methods return the full alignment diagnostics.

    Parameters
    -------------
    log
        Event log
    args
        Specification of the process model
    multi_processing
        Boolean value that enables the multiprocessing (default: False)

    Returns
    -------------
    aligned_traces
        A list of alignments for each trace of the log (in the same order as the traces in the event log)
    """
    if len(args) == 3:
        if type(args[0]) is PetriNet:
            # Petri net alignments
            from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
            if multi_processing:
                return alignments.apply_multiprocessing(log, args[0], args[1], args[2], parameters=get_properties(log))
            else:
                return alignments.apply(log, args[0], args[1], args[2], parameters=get_properties(log))
        elif type(args[0]) is dict or type(args[0]) is Counter:
            # DFG alignments
            from pm4py.algo.conformance.alignments.dfg import algorithm as dfg_alignment
            return dfg_alignment.apply(log, args[0], args[1], args[2], parameters=get_properties(log))
    elif len(args) == 1:
        if type(args[0]) is ProcessTree:
            # process tree alignments
            from pm4py.algo.conformance.alignments.process_tree.variants import search_graph_pt
            if multi_processing:
                return search_graph_pt.apply_multiprocessing(log, args[0], parameters=get_properties(log))
            else:
                return search_graph_pt.apply(log, args[0], parameters=get_properties(log))
    # try to convert to Petri net
    import pm4py
    from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
    net, im, fm = pm4py.convert_to_petri_net(*args)
    if multi_processing:
        return alignments.apply_multiprocessing(log, net, im, fm, parameters=get_properties(log))
    else:
        return alignments.apply(log, net, im, fm, parameters=get_properties(log))


@deprecation.deprecated(deprecated_in='2.2.2', removed_in='2.4.0',
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
    from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
    return alignments.apply(log, petri_net, initial_marking, final_marking, parameters=get_properties(log))


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
    from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness
    return replay_fitness.apply(log, petri_net, initial_marking, final_marking,
                                variant=replay_fitness.Variants.TOKEN_BASED, parameters=get_properties(log))


@deprecation.deprecated(deprecated_in='2.2.2', removed_in='2.4.0',
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
    from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness
    return replay_fitness.apply(log, petri_net, initial_marking, final_marking,
                                variant=replay_fitness.Variants.TOKEN_BASED, parameters=get_properties(log))


def fitness_alignments(log: EventLog, petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, multi_processing: bool = False) -> \
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
    multi_processing
        Boolean value that enables the multiprocessing (default: False)

    Returns
    ---------------
    fitness_dictionary
        dictionary describing average fitness (key: average_trace_fitness) and the percentage of fitting traces (key: percentage_of_fitting_traces)
    """
    from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness
    parameters = get_properties(log)
    parameters["multiprocessing"] = multi_processing
    return replay_fitness.apply(log, petri_net, initial_marking, final_marking,
                                variant=replay_fitness.Variants.ALIGNMENT_BASED, parameters=parameters)


@deprecation.deprecated(deprecated_in='2.2.2', removed_in='2.4.0',
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
    from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness
    return replay_fitness.apply(log, petri_net, initial_marking, final_marking,
                                variant=replay_fitness.Variants.ALIGNMENT_BASED, parameters=get_properties(log))


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
    from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
    return precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN, parameters=get_properties(log))


@deprecation.deprecated(deprecated_in='2.2.2', removed_in='2.4.0',
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
    from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
    return precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN, parameters=get_properties(log))


def precision_alignments(log: EventLog, petri_net: PetriNet, initial_marking: Marking,
                         final_marking: Marking, multi_processing: bool = False) -> float:
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
    multi_processing
        Boolean value that enables the multiprocessing (default: False)

    Returns
    --------------
    precision
        float representing the precision value
    """
    from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
    parameters = get_properties(log)
    parameters["multiprocessing"] = multi_processing
    return precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE,
                                     parameters=parameters)


@deprecation.deprecated(deprecated_in='2.2.2', removed_in='2.4.0',
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
    from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
    return precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE, parameters=get_properties(log))


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


def __check_is_fit_process_tree(trace, tree, activity_key=xes_constants.DEFAULT_NAME_KEY):
    """
    Check if a trace object is fit against a process tree model

    Parameters
    -----------------
    trace
        Trace
    tree
        Process tree
    activity_key
        Activity key (optional)

    Returns
    -----------------
    is_fit
        Boolean value (True if the trace fits; False if the trace does not)
    """
    from pm4py.discovery import discover_footprints
    log = EventLog()
    log.append(trace)
    fp_tree = discover_footprints(tree)
    fp_log = discover_footprints(log)
    fp_conf_res = conformance_diagnostics_footprints(fp_log, fp_tree)[0]
    # CHECK 1) if footprints already say is not fit, then return False
    # (if they say True, it might be a false positive)
    if not fp_conf_res["is_footprints_fit"]:
        return False
    else:
        from pm4py.convert import convert_to_petri_net
        net, im, fm = convert_to_petri_net(tree)
        tbr_conf_res = conformance_diagnostics_token_based_replay(log, net, im, fm)[0]
        # CHECK 2) if TBR says that is fit, then return True
        # (if they say False, it might be a false negative)
        if tbr_conf_res["trace_is_fit"]:
            return True
        else:
            # CHECK 3) alignments definitely say if the trace is fit or not if the previous methods fail
            align_conf_res = conformance_diagnostics_alignments(log, tree)[0]
            return align_conf_res["fitness"] == 1.0


def __check_is_fit_petri_net(trace, net, im, fm, activity_key=xes_constants.DEFAULT_NAME_KEY):
    """
    Checks if a trace object is fit against Petri net object

    Parameters
    ----------------
    trace
        Trace
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    activity_key
        Activity key (optional)

    Returns
    -----------------
    is_fit
        Boolean value (True if the trace fits; False if the trace does not)
    """
    # avoid checking footprints on Petri net (they are too slow)
    activities_model = set(trans.label for trans in net.transitions if trans.label is not None)
    activities_trace = set([x[activity_key] for x in trace])
    diff = activities_trace.difference(activities_model)
    if diff:
        # CHECK 1) there are activities in the trace that are not in the model
        return False
    else:
        log = EventLog()
        log.append(trace)
        tbr_conf_res = conformance_diagnostics_token_based_replay(log, net, im, fm)[0]
        # CHECK 2) if TBR says that is fit, then return True
        # (if they say False, it might be a false negative)
        if tbr_conf_res["trace_is_fit"]:
            return True
        else:
            # CHECK 3) alignments definitely say if the trace is fit or not if the previous methods fail
            align_conf_res = conformance_diagnostics_alignments(log, net, im, fm)[0]
            return align_conf_res["fitness"] == 1.0


def check_is_fitting(*args, activity_key=xes_constants.DEFAULT_NAME_KEY):
    """
    Checks if a trace object is fit against a process model

    Parameters
    -----------------
    trace
        Trace object (trace / variant)
    model
        Model (process tree, Petri net, BPMN, ...)
    activity_key
        Activity key (optional)

    Returns
    -----------------
    is_fit
        Boolean value (True if the trace fits; False if the trace does not)
    """
    from pm4py.util import variants_util
    from pm4py.convert import convert_to_process_tree, convert_to_petri_net

    trace = args[0]
    model = args[1:]

    try:
        model = convert_to_process_tree(*model)
    except:
        # the model cannot be expressed as a process tree, let's say if at least can be expressed as a Petri net
        model = convert_to_petri_net(*model)

    if not isinstance(trace, Trace):
        activities = variants_util.get_activities_from_variant(trace)
        trace = Trace()
        for act in activities:
            trace.append(Event({activity_key: act}))

    if isinstance(model, ProcessTree):
        return __check_is_fit_process_tree(trace, model, activity_key=activity_key)
    elif isinstance(model, tuple) and isinstance(model[0], PetriNet):
        return __check_is_fit_petri_net(trace, model[0], model[1], model[2], activity_key=activity_key)
