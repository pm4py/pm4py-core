import copy


def is_enabled(t, pn, m):
    """
    Verifies whether a given transition is enabled in a given Petri net and marking

    Parameters
    ----------
    :param t: transition to check
    :param pn: Petri net
    :param m: marking to check

    Returns
    -------
    :return: true if enabled, false otherwise
    """

    if t not in pn.transitions:
        return False
    else:
        for a in t.in_arcs:
            if m[a.source] < a.weight:
                return False
    return True


def execute(t, pn, m):
    """
    Executes a given transition in a given Petri net and Marking

    Parameters
    ----------
    :param t: transition to execute
    :param pn: Petri net
    :param m: marking to use

    Returns
    -------
    :return: newly reached marking if :param t: is enabled, None otherwise
    """

    if not is_enabled(t, pn, m):
        return None

    m_out = copy.copy(m)
    for a in t.in_arcs:
        m_out[a.source] -= a.weight
        if m_out[a.source] == 0:
            del m_out[a.source]

    for a in t.out_arcs:
        m_out[a.target] += a.weight

    return m_out


def weak_execute(t, m):
    """
    Execute a transition even if it is not fully enabled

    Parameters
    ----------
    :param t: transition to execute
    :param m: marking to use

    Returns
    -------
    :return: newly reached marking if :param t: is enabled, None otherwise
    """

    m_out = copy.copy(m)
    for a in t.in_arcs:
        m_out[a.source] -= a.weight
        if m_out[a.source] <= 0:
            del m_out[a.source]
    for a in t.out_arcs:
        m_out[a.target] += a.weight
    return m_out


def enabled_transitions(pn, m):
    """
    Returns a set of enabled transitions in a Petri net and given marking

    Parameters
    ----------
    :param pn: Petri net
    :param m: marking of the pn

    Returns
    -------
    :return: set of enabled transitions
    """
    enabled = set()
    for t in pn.transitions:
        if is_enabled(t, pn, m):
            enabled.add(t)
    return enabled
