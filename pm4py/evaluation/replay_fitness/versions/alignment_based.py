import multiprocessing as mp

from pm4py import log as log_lib
from pm4py.algo import alignments
from pm4py.models import petri

PARAM_ACTIVITY_KEY = 'activity_key'

PARAMETERS = [PARAM_ACTIVITY_KEY]


def apply(log, petri_net, initial_marking, final_marking, parameters=None):
    activity_key = parameters[
        PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY
    best_worst = alignments.versions.state_equation_a_star.apply(log_lib.log.Trace(), petri_net, initial_marking,
                                                                 final_marking)
    best_worst_costs = best_worst['cost'] // alignments.utils.STD_MODEL_LOG_MOVE_COST
    with mp.Pool(max(1, mp.cpu_count() - 1)) as pool:
        return pool.starmap(apply_trace, map(
            lambda tr: (tr, petri_net, initial_marking, final_marking, best_worst_costs, activity_key), log))


def apply_trace(trace, petri_net, initial_marking, final_marking, best_worst, activity_key):
    '''
    Performs the basic alignment search, given a trace, a net and the costs of the \"best of the worst\".
    The costs of the best of the worst allows us to deduce the fitness of the trace.
    We compute the fitness by means of 1 - alignment costs / best of worst costs (i.e. costs of 0 => fitness 1)

    Parameters
    ----------
    trace: :class:`list` input trace, assumed to be a list of events (i.e. the code will use the activity key to get the activities)
    petri_net: :class:`pm4py.models.petri.net.PetriNet` the Petri net to use in the alignment
    initial_marking: :class:`pm4py.models.petri.net.Marking` initial marking in the Petri net
    final_marking: :class:`pm4py.models.petri.net.Marking` final marking in the Petri net
    activity_key: :class:`str` (optional) key to use to identify the activity described by the events

    Returns
    -------
    dictionary: `dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and **traversed_arcs**
    '''
    alignment = alignments.versions.state_equation_a_star.apply(trace, petri_net, initial_marking, final_marking, {
        alignments.versions.state_equation_a_star.PARAM_ACTIVITY_KEY: activity_key})
    fixed_costs = alignment['cost'] // alignments.utils.STD_MODEL_LOG_MOVE_COST
    fitness = 1 - (fixed_costs / best_worst)
    return {'trace': trace, 'alignment': alignment['alignment'], 'cost': fixed_costs, 'fitness': fitness,
            'visited_states': alignment['visited_states'], 'queued_states': alignment['queued_states'],
            'traversed_arcs': alignment['traversed_arcs']}
