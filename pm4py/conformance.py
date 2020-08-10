def conformance_tbr(log, petri_net, initial_marking, final_marking):
    """
    Apply token-based replay

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


def conformance_alignments(log, petri_net, initial_marking, final_marking):
    """
    Apply the alignments algorithm between a log and a Petri net

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


def evaluate_fitness_tbr(log, petri_net, initial_marking, final_marking):
    """
    Calculates the fitness using token-based replay

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


def evaluate_fitness_alignments(log, petri_net, initial_marking, final_marking):
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


def evaluate_precision_tbr(log, petri_net, initial_marking, final_marking):
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
    precision_dictionary
        Precision dictionary (from TBR)
    """
    from pm4py.evaluation.precision import evaluator as precision_evaluator
    return precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)


def evaluate_precision_alignments(log, petri_net, initial_marking, final_marking):
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
    precision_dictionary
        Precision dictionary (from alignments)
    """
    from pm4py.evaluation.precision import evaluator as precision_evaluator
    return precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE)
