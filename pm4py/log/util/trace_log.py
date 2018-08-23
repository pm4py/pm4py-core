from pm4py.log.util import xes as xes_util


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

def get_trace_variants(log, key=xes_util.DEFAULT_NAME_KEY):
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


def project_traces(trace_log, keys=xes_util.DEFAULT_NAME_KEY):
    '''
    projects traces on a (set of) event attribute key(s).
    If the key provided is of type string, each trace is converted into a list of strings.
    If the key provided is a collection, each trace is converted into a list of (smaller) dicts of key value pairs

    :param trace_log:
    :param keys:
    :return:
    '''
    if isinstance(keys, str):
        return list(map(lambda t: list(map(lambda e: e[keys], t)), trace_log))
    else:
        return list(map(lambda t: list(map(lambda e: {key: e[key] for key in keys}))))



