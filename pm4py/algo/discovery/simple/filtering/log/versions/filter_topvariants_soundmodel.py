from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.log import EventLog
from pm4py.objects.petri import check_soundness


def apply(log, parameters=None):
    """
    Returns a log from which a sound workflow net could be extracted taking into account
    a discovery algorithm returning models only with visible transitions

    Parameters
    ------------
    log
        Trace log
    parameters
        Possible parameters of the algorithm, including:
            discovery_algorithm -> Discovery algorithm to consider, possible choices: alphaclassic
            max_no_variants -> Maximum number of variants to consider to return a Petri net
            variants_list - > List of variants to use
    Returns
    ------------
    filtered_log
        Filtered log
    """
    from pm4py.evaluation.replay_fitness import factory as replay_fitness_factory

    if parameters is None:
        parameters = {}
    discovery_algorithm = parameters["discovery_algorithm"] if "discovery_algorithm" in parameters else "alphaclassic"
    max_no_variants = parameters["max_no_variants"] if "max_no_variants" in parameters else 7
    all_variants_list = parameters["variants_list"] if "all_variants_list" in parameters else None
    if all_variants_list is None:
        all_variants_dictio = variants_filter.get_variants(log, parameters=parameters)
        all_variants_list = []
        for var in all_variants_dictio:
            all_variants_list.append([var, len(all_variants_dictio[var])])
    all_variants_list = sorted(all_variants_list, key=lambda x: (x[1], x[0]), reverse=True)
    considered_variants = []
    considered_traces = []

    i = 0
    while i < min(len(all_variants_list), max_no_variants):
        variant = all_variants_list[i][0]

        considered_variants.append(variant)
        considered_traces.append(all_variants_dictio[variant][0])
        filtered_log = EventLog(considered_traces)
        net = None
        initial_marking = None
        final_marking = None
        if discovery_algorithm == "alphaclassic" or discovery_algorithm == "alpha":
            net, initial_marking, final_marking = alpha_miner.apply(filtered_log, parameters=parameters)
        is_sound = check_soundness.check_petri_wfnet_and_soundness(net)
        if not is_sound:
            del considered_variants[-1]
            del considered_traces[-1]
        else:
            try:
                fitness = replay_fitness_factory.apply(filtered_log, net, initial_marking, final_marking,
                                                       parameters=parameters)
                if fitness["log_fitness"] < 0.99999:
                    del considered_variants[-1]
                    del considered_traces[-1]
            except TypeError:
                del considered_variants[-1]
                del considered_traces[-1]
        i = i + 1

    sound_log = EventLog()
    if considered_variants:
        sound_log = variants_filter.apply(log, considered_variants, parameters=parameters)

    return sound_log
