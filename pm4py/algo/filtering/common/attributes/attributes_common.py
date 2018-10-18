def get_sorted_attributes_list(attributes):
    """
    Gets sorted attributes list

    Parameters
    ----------
    attributes
        Dictionary of attributes associated with their count

    Returns
    ----------
    listact
        Sorted end attributes list
    """
    listattr = []
    for a in attributes:
        listattr.append([a, attributes[a]])
    listattr = sorted(listattr, key=lambda x: x[1], reverse=True)
    return listattr


def get_attributes_threshold(alist, decreasing_factor, min_activity_count=1, max_activity_count=25):
    """
    Get attributes cutting threshold

    Parameters
    ----------
    alist
        Sorted attributes list
    decreasing_factor
        Decreasing factor of the algorithm
    min_activity_count
        Minimum number of activities to include
    max_activity_count
        Maximum number of activities to include

    Returns
    ---------
    threshold
        Activities cutting threshold
    """
    index = max(0, min(min_activity_count - 1, len(alist) - 1))
    threshold = alist[index][1]
    index = index + 1
    for i in range(index, len(alist)):
        value = alist[i][1]
        if value > threshold * decreasing_factor:
            threshold = value
        if i >= max_activity_count:
            break
    return threshold
