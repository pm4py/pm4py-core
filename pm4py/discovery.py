def discover_dfg(log):
    """
    Discovers a DFG from a log

    Parameters
    --------------
    log
        Event log

    Returns
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
    dfg = dfg_discovery.apply(log)
    from pm4py.statistics.start_activities.log import get as start_activities_module
    from pm4py.statistics.end_activities.log import get as end_activities_module
    start_activities = start_activities_module.get_start_activities(log)
    end_activities = end_activities_module.get_end_activities(log)
    return dfg, start_activities, end_activities


def discover_petri_net_alpha(log):
    """
    Discovers a Petri net using the Alpha Miner

    Parameters
    --------------
    log
        Event log

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    from pm4py.algo.discovery.alpha import algorithm as alpha_miner
    return alpha_miner.apply(log, variant=alpha_miner.Variants.ALPHA_VERSION_CLASSIC)


def discover_petri_net_alpha_plus(log):
    """
    Discovers a Petri net using the Alpha+ algorithm

    Parameters
    --------------
    log
        Event log

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    from pm4py.algo.discovery.alpha import algorithm as alpha_miner
    return alpha_miner.apply(log, variant=alpha_miner.Variants.ALPHA_VERSION_PLUS)


def discover_petri_net_inductive(log, noise_threshold=0.0):
    """
    Discovers a Petri net using the IMDFc algorithm

    Parameters
    --------------
    log
        Event log
    noise_threshold
        Noise threshold (default: 0.0)

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    from pm4py.algo.discovery.inductive import algorithm as inductive_miner
    return inductive_miner.apply(log, variant=inductive_miner.Variants.DFG_BASED, parameters={
        inductive_miner.Variants.DFG_BASED.value.Parameters.NOISE_THRESHOLD: noise_threshold})


def discover_petri_net_heuristics(log, dependency_threshold=0.5, and_threshold=0.65, loop_two_threshold=0.5):
    """
    Discover a Petri net using the Heuristics Miner

    Parameters
    ---------------
    log
        Event log
    dependency_threshold
        Dependency threshold (default: 0.5)
    and_threshold
        AND threshold (default: 0.65)
    loop_two_threshold
        Loop two threshold (default: 0.5)

    Returns
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
    parameters = heuristics_miner.Variants.CLASSIC.value.Parameters
    return heuristics_miner.apply(log, variant=heuristics_miner.Variants.CLASSIC, parameters={
        parameters.DEPENDENCY_THRESH: dependency_threshold, parameters.AND_MEASURE_THRESH: and_threshold,
        parameters.LOOP_LENGTH_TWO_THRESH: loop_two_threshold})


def discover_tree_inductive(log, noise_threshold=0.0):
    """
    Discovers a process tree using the IMDFc algorithm

    Parameters
    --------------
    log
        Event log
    noise_threshold
        Noise threshold (default: 0.0)

    Returns
    --------------
    process_tree
        Process tree object
    """
    from pm4py.algo.discovery.inductive import algorithm as inductive_miner
    return inductive_miner.apply_tree(log, variant=inductive_miner.Variants.DFG_BASED, parameters={
        inductive_miner.Variants.DFG_BASED.value.Parameters.NOISE_THRESHOLD: noise_threshold})


def discover_heuristics_net(log, dependency_threshold=0.5, and_threshold=0.65, loop_two_threshold=0.5):
    """
    Discovers an heuristics net

    Parameters
    ---------------
    log
        Event log
    dependency_threshold
        Dependency threshold (default: 0.5)
    and_threshold
        AND threshold (default: 0.65)
    loop_two_threshold
        Loop two threshold (default: 0.5)

    Returns
    --------------
    heu_net
        Heuristics net
    """
    from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
    parameters = heuristics_miner.Variants.CLASSIC.value.Parameters
    return heuristics_miner.apply_heu(log, variant=heuristics_miner.Variants.CLASSIC, parameters={
        parameters.DEPENDENCY_THRESH: dependency_threshold, parameters.AND_MEASURE_THRESH: and_threshold,
        parameters.LOOP_LENGTH_TWO_THRESH: loop_two_threshold})
