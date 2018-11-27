from pm4py.algo.filtering.tracelog.variants import variants_filter
from pm4py.algo.discovery.alpha import factory as alpha_miner
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

    Returns
    ------------
    filtered_log
        Filtered trace log
    """
    if parameters is None:
        parameters = {}
    discovery_algorithm = parameters["discovery_algorithm"] if "discovery_algorithm" in parameters else "alphaclassic"
    max_no_variants = parameters["max_no_variants"] if "max_no_variants" in parameters else 10
    all_variants_dictio = variants_filter.get_variants(log, parameters=parameters)
    all_variants_list = []
    for var in all_variants_dictio:
        all_variants_list.append([var, len(all_variants_dictio[var])])
    all_variants_list = sorted(all_variants_list, key=lambda x: x[1], reverse=True)
    considered_variants = []
    sound_log = None
    i = 0
    while i < min(len(all_variants_list), max_no_variants):
        variant = all_variants_list[i][0]
        considered_variants.append(variant)
        filtered_log = variants_filter.apply(log, considered_variants)
        if discovery_algorithm == "alphaclassic" or discovery_algorithm == "alpha":
            net, initial_marking, final_marking = alpha_miner.apply(filtered_log)
        is_sound = check_soundness.check_petri_wfnet_and_soundness(net)
        if is_sound:
            sound_log = filtered_log
        else:
            break
        i = i + 1
    return sound_log
