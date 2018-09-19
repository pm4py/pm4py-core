def get_outgoing_edges(dfg):
    """
    Gets outgoing edges of the provided DFG graph
    """
    outgoing = {}
    for el in dfg:
        if type(el[0]) is str:
            if not el[0] in outgoing:
                outgoing[el[0]] = {}
            outgoing[el[0]][el[1]] = dfg[el]
        else:
            if not el[0][0] in outgoing:
                outgoing[el[0][0]] = {}
            outgoing[el[0][0]][el[0][1]] = el[1]
    return outgoing


def get_ingoing_edges(dfg):
    """
    Get ingoing edges of the provided DFG graph
    """
    ingoing = {}
    for el in dfg:
        if type(el[0]) is str:
            if not el[1] in ingoing:
                ingoing[el[1]] = {}
            ingoing[el[1]][el[0]] = dfg[el]
        else:
            if not el[0][1] in ingoing:
                ingoing[el[0][1]] = {}
            ingoing[el[0][1]][el[0][0]] = el[1]
    return ingoing

def infer_start_activities(dfg):
    """
    Infer start activities from a Directly-Follows Graph

    Parameters
    ----------
    dfg
        Directly-Follows Graph

    Returns
    ----------
    start_activities
        Start activities in the log
    """
    ingoing = get_ingoing_edges(dfg)
    outgoing = get_outgoing_edges(dfg)

    start_activities = []

    for act in outgoing:
        if not act in ingoing:
            start_activities.append(act)

    return start_activities

def infer_end_activities(dfg):
    """
    Infer end activities from a Directly-Follows Graph

    Parameters
    ----------
    dfg
        Directly-Follows Graph

    Returns
    ----------
    end_activities
        End activities in the log
    """
    ingoing = get_ingoing_edges(dfg)
    outgoing = get_outgoing_edges(dfg)

    end_activities = []

    for act in ingoing:
        if not act in outgoing:
            end_activities.append(act)

    return end_activities