from collections import Counter

def equivalence(trace):
    """
    Get the equivalence relations given a list of activities

    Parameters
    --------------
    trace
        List activities

    Returns
    --------------
    rel
        Relations inside the trace
    """
    ret = set()
    freq = activ_freq(trace)
    for x in freq:
        for y in freq:
            if x != y and freq[x] == freq[y]:
                ret.add((x, y))
                ret.add((y, x))
    return ret


def after(trace):
    """
    Get the after- relations given a list of activities

    Parameters
    --------------
    trace
        List activities

    Returns
    --------------
    rel
        After- inside the trace
    """
    return set((trace[i], trace[j]) for i in range(len(trace)) for j in range(len(trace)) if j > i)


def before(trace):
    """
    Get the before- relations given a list of activities

    Parameters
    --------------
    trace
        List activities

    Returns
    --------------
    rel
        Before- inside the trace
    """
    return set((trace[i], trace[j]) for i in range(len(trace)) for j in range(len(trace)) if j < i)


def combos(trace):
    """
    Get the combinations between all the activities of the trace relations given a list of activities

    Parameters
    --------------
    trace
        List activities

    Returns
    --------------
    rel
        Combos inside the trace
    """
    return set((x, y) for x in trace for y in trace if x != y)


def directly_follows(trace):
    """
    Get the directly-follows relations given a list of activities

    Parameters
    --------------
    trace
        List activities

    Returns
    --------------
    rel
        Directly-follows relations inside the trace
    """
    return set((trace[i], trace[i+1]) for i in range(len(trace)-1))


def activ_freq(trace):
    """
    Gets the frequency of activities happening in a trace

    Parameters
    --------------
    trace
        List activities

    Returns
    --------------
    freq
        Frequency of activities
    """
    return Counter(trace)


def get_trace_info(trace):
    """
    Technical method for conformance checking
    """
    return (equivalence(trace), after(trace), before(trace), combos(trace), directly_follows(trace), activ_freq(trace))
