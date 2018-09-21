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


def get_end_activities_threshold(end_activities, ealist, decreasingFactor):
    """
    Get end attributes cutting threshold

    Parameters
    ----------
    end_activities
        Dictionary of end attributes associated with their count
    ealist
        Sorted end attributes list

    Returns
    ---------
    threshold
        End attributes cutting threshold
    """

    threshold = ealist[0][1]
    i = 1
    while i < len(ealist):
        value = ealist[i][1]
        if value > threshold * decreasingFactor:
            threshold = value
        i = i + 1
    return threshold