from pm4py.models.petri import visualize
from pm4py.algo.tokenreplay import factory as token_replay
from pm4py.algo.tokenreplay.data_structures import performance_map
from pm4py import log as log_lib

PARAM_ACTIVITY_KEY = 'activity_key'
PARAM_TIMESTAMP_KEY = 'timestamp_key'

PARAMETERS = [PARAM_ACTIVITY_KEY, PARAM_TIMESTAMP_KEY]

def get_decorations(log, net, initial_marking, final_marking, parameters=None, measure="frequency"):
    """
    Calculate decorations in order to annotate the Petri net

    Parameters
    -----------
    log
        Trace log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters associated to the algorithm
    measure
        Measure to represent on the process model (frequency/performance)

    Returns
    ------------
    decorations
        Decorations to put on the process model
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[
            PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY
    timestamp_key = parameters[PARAM_TIMESTAMP_KEY] if PARAM_TIMESTAMP_KEY in parameters else "time:timestamp"

    # do the replay
    [traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] = \
        token_replay.apply(log, net, initial_marking, final_marking, activity_key=activity_key)

    element_statistics = performance_map.single_element_statistics(log, net, initial_marking,
                                                                   activatedTransitions,
                                                                   activity_key=activity_key,
                                                                   timestamp_key=timestamp_key)
    aggregated_statistics = performance_map.aggregate_statistics(element_statistics, measure=measure)

    return aggregated_statistics

def apply_frequency(net, initial_marking, final_marking, log=None, parameters=None):
    """
    Apply method for Petri net visualization (useful for recall from factory; it calls the graphviz_visualization method)
    adding frequency representation obtained by token replay

    Parameters
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        (Optional) trace log
    parameters
        Algorithm parameters (including the activity key used during the replay, and the timestamp key)

    Returns
    -----------
    viz
        Graph object
    """
    decorations = None
    if log is not None:
        decorations = get_decorations(log, net, initial_marking, final_marking, parameters=parameters, measure="frequency")
    return visualize.apply(net, initial_marking, final_marking, parameters=parameters, decorations=decorations)

def apply_performance(net, initial_marking, final_marking, log=None, parameters=None):
    """
    Apply method for Petri net visualization (useful for recall from factory; it calls the graphviz_visualization method)
    adding performance representation obtained by token replay

    Parameters
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        (Optional) trace log
    parameters
        Algorithm parameters (including the activity key used during the replay, and the timestamp key)

    Returns
    -----------
    viz
        Graph object
    """
    decorations = None
    if log is not None:
        decorations = get_decorations(log, net, initial_marking, final_marking, parameters=parameters, measure="performance")
    return visualize.apply(net, initial_marking, final_marking, parameters=parameters, decorations=decorations)