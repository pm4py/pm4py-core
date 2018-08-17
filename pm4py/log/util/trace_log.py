
#TODO: we can do some instance checking and then support both trace level and event level logs..
def get_event_labels(log, key):
    '''
    Fetches the labels present in a trace log, given a key to use within the events.

    Parameters
    ----------
    :param log: trace log to use
    :param key: to use for event identification, can for example  be "concept:name"

    Returns
    -------
    :return: a list of labels
    '''
    labels = []
    for t in log:
        for e in t:
            if key in e and e[key] not in labels:
                labels.append(e[key])
    return labels

def get_trace_variants(log, key='concept:name'):
    '''
    Returns a pair of a list of (variants, dict[index -> trace]) where the index of a variant maps to all traces describing that variant, with that key.

    Parameters
    ---------
    :param log: trace log
    :param key: key to use to identify the label of an event

    Returns
    -------
    :return:
    '''
    variants = []
    variant_map = dict()
    for t in log:
        variant = list(map(lambda e: e[key], t))
        for i in range(0, len(variants)):
            if variants[i] == variant:
                variant_map[i].append(t)
                continue
        variant_map[len(variants)] = [t]
        variants.append(variant)
    return (variants, variant_map)

