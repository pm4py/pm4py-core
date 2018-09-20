from pm4py.algo.conformance.tokenreplay import factory as token_replay
from pm4py.entities import log as log_lib
from pm4py import util as pmutil
from pm4py.entities.log.util import xes as xes_util

PARAM_ACTIVITY_KEY = xes_util.DEFAULT_NAME_KEY

PARAMETERS = [PARAM_ACTIVITY_KEY]

def get_fitness(aligned_traces):
    """
    Gets a dictionary expressing fitness in a synthetic way from the list of boolean values
    saying if a trace in the log is fit, and the float values of fitness associated to each trace

    Parameters
    ------------
    aligned_traces
        Result of the token-based replayer

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
    activity_key = parameters[PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY

    parameters_TR = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}

    aligned_traces = token_replay.apply(log, petri_net, initial_marking, final_marking, parameters=parameters_TR)

    return get_fitness(aligned_traces)

