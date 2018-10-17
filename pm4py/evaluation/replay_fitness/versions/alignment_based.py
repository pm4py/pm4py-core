import multiprocessing as mp

import pm4py
from pm4py.algo.conformance import alignments
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import apply as apply_alignments
from pm4py.objects import log as log_lib
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY

DEFAULT_NAME_KEY = log_lib.util.xes.DEFAULT_NAME_KEY


def evaluate(aligned_traces, parameters=None):
    """
    Transforms the alignment result to a simple dictionary
    including the percentage of fit traces and the average fitness

    Parameters
    ----------
    aligned_traces
        Alignments calculated for the traces in the log
    parameters
        Possible parameters of the evaluation

    Returns
    ----------
    dictionary
        Containing two keys (percFitTraces and averageFitness)
    """
    if parameters is None:
        parameters = {}
    str(parameters)
    no_traces = len(aligned_traces)
    no_fit_traces = 0
    sum_fitness = 0.0

    for tr in aligned_traces:
        if tr["fitness"] == 1.0:
            no_fit_traces = no_fit_traces + 1
        sum_fitness = sum_fitness + tr["fitness"]

    perc_fit_traces = 0.0
    average_fitness = 0.0

    if no_traces > 0:
        perc_fit_traces = (100.0 * float(no_fit_traces)) / (float(no_traces))
        average_fitness = float(sum_fitness) / float(no_traces)

    return {"percFitTraces": perc_fit_traces, "averageFitness": average_fitness}


def apply(log, petri_net, initial_marking, final_marking, parameters=None):
    if parameters is None:
        parameters = {}
    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    best_worst = pm4py.algo.conformance.alignments.versions.state_equation_a_star.apply(log_lib.log.Trace(), petri_net,
                                                                                        initial_marking,
                                                                                        final_marking)
    best_worst_costs = best_worst['cost'] // alignments.utils.STD_MODEL_LOG_MOVE_COST
    with mp.Pool(max(1, mp.cpu_count() - 1)) as pool:
        alignment_result = pool.starmap(apply_trace, map(
            lambda tr: (tr, petri_net, initial_marking, final_marking, best_worst_costs, activity_key), log))

        return evaluate(alignment_result)


def apply_trace(trace, petri_net, initial_marking, final_marking, best_worst, activity_key):
    """
    Performs the basic alignment search, given a trace, a net and the costs of the \"best of the worst\".
    The costs of the best of the worst allows us to deduce the fitness of the trace.
    We compute the fitness by means of 1 - alignment costs / best of worst costs (i.e. costs of 0 => fitness 1)

    Parameters
    ----------
    trace: :class:`list` input trace, assumed to be a list of events (i.e. the code will use the activity key to
    get the attributes)
    petri_net: :class:`pm4py.objects.petri.net.PetriNet` the Petri net to use in the alignment
    initial_marking: :class:`pm4py.objects.petri.net.Marking` initial marking in the Petri net
    final_marking: :class:`pm4py.objects.petri.net.Marking` final marking in the Petri net
    best_worst: cost of the best worst alignment of a trace (empty trace aligned to the model)
    activity_key: :class:`str` (optional) key to use to identify the activity described by the events

    Returns
    -------
    dictionary: `dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and **traversed_arcs**
    """
    alignment = apply_alignments(trace, petri_net, initial_marking, final_marking,
                                 {PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key})
    fixed_costs = alignment['cost'] // alignments.utils.STD_MODEL_LOG_MOVE_COST
    if best_worst > 0:
        fitness = 1 - (fixed_costs / best_worst)
    else:
        fitness = 1
    return {'trace': trace, 'alignment': alignment['alignment'], 'cost': fixed_costs, 'fitness': fitness,
            'visited_states': alignment['visited_states'], 'queued_states': alignment['queued_states'],
            'traversed_arcs': alignment['traversed_arcs']}
