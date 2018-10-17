def get_sorted_start_activities_list(start_activities):
    """
    Gets sorted start attributes list

    Parameters
    ----------
    start_activities
        Dictionary of start attributes associated with their count

    Returns
    ----------
    listact
        Sorted start attributes list
    """
    listact = []
    for sa in start_activities:
        listact.append([sa, start_activities[sa]])
    listact = sorted(listact, key=lambda x: x[1], reverse=True)
    return listact


def get_start_activities_threshold(salist, decreasing_factor):
    """
    Get start attributes cutting threshold

    Parameters
    ----------
    salist
        Sorted start attributes list
    decreasing_factor
        Decreasing factor of the algorithm

    Returns
    ---------
    threshold
        Start attributes cutting threshold
    """
    threshold = salist[0][1]
    for i in range(1, len(salist)):
        value = salist[i][1]
        if value > threshold * decreasing_factor:
            threshold = value
    return threshold
