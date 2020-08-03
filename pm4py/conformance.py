def conformance_tbr(log, petri_net):
    """
    Apply token-based replay

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net

    Returns
    --------------
    replay_results
        A list of replay results for each trace of the log
    """
    net, im, fm = petri_net
    from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
    return token_replay.apply(log, net, im, fm)


def conformance_alignments(log, petri_net):
    """
    Apply the alignments algorithm between a log and a Petri net

    Parameters
    -------------
    log
        Event log
    petri_net
        Petri net

    Returns
    -------------
    aligned_traces
        A list of alignments for each trace of the log
    """
    net, im, fm = petri_net
    from pm4py.algo.conformance.alignments import algorithm as alignments
    return alignments.apply(log, net, im, fm)


def evaluate_fitness_tbr(log, petri_net):
    """
    Calculates the fitness using token-based replay

    Parameters
    ---------------
    log
        Event log
    petri_net
        Petri net object

    Returns
    ---------------
    fitness_dictionary
        Fitness dictionary (from TBR)
    """
    net, im, fm = petri_net
    from pm4py.evaluation.replay_fitness import evaluator as replay_fitness
    return replay_fitness.apply(log, net, im, fm, variant=replay_fitness.Variants.TOKEN_BASED)


def evaluate_fitness_alignments(log, petri_net):
    """
    Calculates the fitness using alignments

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net object

    Returns
    ---------------
    fitness_dictionary
        Fitness dictionary (from alignments)
    """
    net, im, fm = petri_net
    from pm4py.evaluation.replay_fitness import evaluator as replay_fitness
    return replay_fitness.apply(log, net, im, fm, variant=replay_fitness.Variants.ALIGNMENT_BASED)


def evaluate_precision_tbr(log, petri_net):
    """
    Calculates the precision using token-based replay

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net object

    Returns
    --------------
    precision_dictionary
        Precision dictionary (from TBR)
    """
    net, im, fm = petri_net
    from pm4py.evaluation.precision import evaluator as precision_evaluator
    return precision_evaluator.apply(log, net, im, fm, variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)


def evaluate_precision_alignments(log, petri_net):
    """
    Calculates the precision using alignments

    Parameters
    --------------
    log
        Event log
    petri_net
        Petri net object

    Returns
    --------------
    precision_dictionary
        Precision dictionary (from alignments)
    """
    net, im, fm = petri_net
    from pm4py.evaluation.precision import evaluator as precision_evaluator
    return precision_evaluator.apply(log, net, im, fm, variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE)
