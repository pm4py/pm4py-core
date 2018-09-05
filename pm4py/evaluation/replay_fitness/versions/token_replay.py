from pm4py.algo.tokenreplay import factory as token_replay
from pm4py import log as log_lib

PARAM_ACTIVITY_KEY = 'activity_key'

PARAMETERS = [PARAM_ACTIVITY_KEY]

def apply(log, petri_net, initial_marking, final_marking, parameters=None):
    """
    Apply token replay fitness evaluation

    Parameters
    -----------
    log
        Trace log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters

    Returns
    -----------
    dictionary
        Containing two keys (percFitTraces and averageFitness)
    """

    if parameters is None:
        parameters = {}
    activity_key = parameters[PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY
    [traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] =\
        token_replay.apply(log, petri_net, initial_marking, final_marking, activity_key=activity_key)
    noTraces = len(traceIsFit)
    fitTraces = len([x for x in traceIsFit if x])
    sumOfFitness = sum(traceFitnessValue)
    percFitTraces = 0.0
    averageFitness = 0.0
    if noTraces > 0:
        percFitTraces = float(100.0 * fitTraces)/float(noTraces)
        averageFitness = float(sumOfFitness)/float(noTraces)
    return {"percFitTraces": percFitTraces, "averageFitness": averageFitness}

