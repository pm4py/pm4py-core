import multiprocessing as mp

from pm4py.entities import log as log_lib
from pm4py.algo.conformance import alignments
from pm4py.entities.log.util import xes as xes_util

PARAM_ACTIVITY_KEY = xes_util.DEFAULT_NAME_KEY

PARAMETERS = [PARAM_ACTIVITY_KEY]

def transform_align_result_to_simple_dictionary(alignResults):
    """
    Transforms the alignment result to a simple dictionary
    including the percentage of fit traces and the average fitness

    Parameters
    ----------
    alignResults
        Alignments calculated for the traces in the log

    Returns
    ----------
    dictionary
        Containing two keys (percFitTraces and averageFitness)
    """
    noTraces = len(alignResults)
    noFitTraces = 0
    sumFitness = 0.0

    for tr in alignResults:
        if tr["fitness"] == 1.0:
            noFitTraces = noFitTraces + 1
        sumFitness = sumFitness + tr["fitness"]

    percFitTraces = 0.0
    averageFitness = 0.0

    if noTraces > 0:
        percFitTraces = (100.0 * float(noFitTraces))/(float(noTraces))
        averageFitness = float(sumFitness)/float(noTraces)

    return {"percFitTraces": percFitTraces, "averageFitness": averageFitness}

def apply(log, petri_net, initial_marking, final_marking, parameters=None):
    if parameters is None:
        parameters = {}
    activity_key = parameters[
        PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY
    best_worst = pm4py.algo.conformance.alignments.versions.state_equation_a_star.apply(log_lib.log.Trace(), petri_net, initial_marking,
                                                                                        final_marking)
    best_worst_costs = best_worst['cost'] // alignments.utils.STD_MODEL_LOG_MOVE_COST
    with mp.Pool(max(1, mp.cpu_count() - 1)) as pool:
        alignmentResult = pool.starmap(apply_trace, map(
            lambda tr: (tr, petri_net, initial_marking, final_marking, best_worst_costs, activity_key), log))

        return transform_align_result_to_simple_dictionary(alignmentResult)

def apply_trace(trace, petri_net, initial_marking, final_marking, best_worst, activity_key):
    '''
    Performs the basic alignment search, given a trace, a net and the costs of the \"best of the worst\".
    The costs of the best of the worst allows us to deduce the fitness of the trace.
    We compute the fitness by means of 1 - alignment costs / best of worst costs (i.e. costs of 0 => fitness 1)

    Parameters
    ----------
    trace: :class:`list` input trace, assumed to be a list of events (i.e. the code will use the activity key to get the attributes)
    petri_net: :class:`pm4py.entities.petri.net.PetriNet` the Petri net to use in the alignment
    initial_marking: :class:`pm4py.entities.petri.net.Marking` initial marking in the Petri net
    final_marking: :class:`pm4py.entities.petri.net.Marking` final marking in the Petri net
    activity_key: :class:`str` (optional) key to use to identify the activity described by the events

    Returns
    -------
    dictionary: `dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and **traversed_arcs**
    '''
    alignment = pm4py.algo.conformance.alignments.versions.state_equation_a_star.apply(trace, petri_net, initial_marking, final_marking, {
        pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_ACTIVITY_KEY: activity_key})
    fixed_costs = alignment['cost'] // alignments.utils.STD_MODEL_LOG_MOVE_COST
    fitness = 1 - (fixed_costs / best_worst)
    return {'trace': trace, 'alignment': alignment['alignment'], 'cost': fixed_costs, 'fitness': fitness,
            'visited_states': alignment['visited_states'], 'queued_states': alignment['queued_states'],
            'traversed_arcs': alignment['traversed_arcs']}
