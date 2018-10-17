from pm4py.evaluation.replay_fitness.versions import alignment_based, token_replay

ALIGNMENT_BASED = "alignments"
TOKEN_BASED = "token_replay"
VERSIONS = {ALIGNMENT_BASED: alignment_based.apply, TOKEN_BASED: token_replay.apply}
VERSIONS_EVALUATION = {ALIGNMENT_BASED: alignment_based.evaluate, TOKEN_BASED: token_replay.evaluate}

PARAM_ACTIVITY_KEY = 'activity_key'


def apply(log, petri_net, initial_marking, final_marking, parameters=None, variant="token_replay"):
    """
    Apply fitness evaluation starting from an event log and a marked Petri net,
    by using one of the replay techniques provided by PM4Py

    Parameters
    -----------
    log
        Trace log object
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters related to the replay algorithm
    variant
        Chosen variant (alignments or token-based replay)

    Returns
    ----------
    fitness_eval
        Fitness evaluation
    """
    return VERSIONS[variant](log, petri_net, initial_marking, final_marking, parameters=parameters)


def evaluate(results, parameters="None", variant="token_replay"):
    """
    Evaluate replay results when the replay algorithm has already been applied

    Parameters
    -----------
    results
        Results of the replay algorithm
    parameters
        Possible parameters passed to the evaluation
    variant
        Indicates which evaluator is called

    Returns
    -----------
    fitness_eval
        Fitness evaluation
    """
    return VERSIONS_EVALUATION[variant](results, parameters=parameters)
