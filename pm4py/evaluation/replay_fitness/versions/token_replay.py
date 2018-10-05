from pm4py.algo.conformance.tokenreplay import factory as token_replay
from pm4py.objects import log as log_lib
from pm4py import util as pmutil

def evaluate(aligned_traces, parameters=None):
    """
    Gets a dictionary expressing fitness in a synthetic way from the list of boolean values
    saying if a trace in the log is fit, and the float values of fitness associated to each trace

    Parameters
    ------------
    aligned_traces
        Result of the token-based replayer
    parameters
        Possible parameters of the evaluation

    Returns
    -----------
    dictionary
        Containing two keys (percFitTraces and averageFitness)
    """
    noTraces = len(aligned_traces)
    fitTraces = len([x for x in aligned_traces if x["tFit"]])
    sumOfFitness = sum([x["tValue"] for x in aligned_traces])
    percFitTraces = 0.0
    averageFitness = 0.0
    if noTraces > 0:
        percFitTraces = float(100.0 * fitTraces)/float(noTraces)
        averageFitness = float(sumOfFitness)/float(noTraces)
    return {"percFitTraces": percFitTraces, "averageFitness": averageFitness}

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
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY

    parameters_TR = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key, "consider_remaining_in_fitness": True}

    aligned_traces = token_replay.apply(log, petri_net, initial_marking, final_marking, parameters=parameters_TR)

    return evaluate(aligned_traces)

