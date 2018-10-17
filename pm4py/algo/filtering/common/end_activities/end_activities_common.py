def get_sorted_end_activities_list(end_activities):
    """
    Gets sorted end attributes list

    Parameters
    ----------
    end_activities
        Dictionary of end attributes associated with their count

    Returns
    ----------
    listact
        Sorted end attributes list
    """
    listact = []
    for ea in end_activities:
        listact.append([ea, end_activities[ea]])
    listact = sorted(listact, key=lambda x: x[1], reverse=True)
    return listact


def get_end_activities_threshold(ealist, decreasing_factor):
    """
    Get end attributes cutting threshold

    Parameters
    ----------
    ealist
        Sorted end attributes list
    decreasing_factor
        Decreasing factor of the algorithm

    Returns
    ---------
    threshold
        End attributes cutting threshold
    """

    threshold = ealist[0][1]
    for i in range(1, len(ealist)):
        value = ealist[i][1]
        if value > threshold * decreasing_factor:
            threshold = value
    return threshold
