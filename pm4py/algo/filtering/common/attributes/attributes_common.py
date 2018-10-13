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


def get_attributes_threshold(attributes, alist, decreasing_factor, min_activity_count = 1, max_activity_count = 25):
    """
    Get attributes cutting threshold

    Parameters
    ----------
    attributes
        Dictionary of attributes associated with their count
    alist
        Sorted attributes list

    Returns
    ---------
    threshold
        Activities cutting threshold
    """

    i = max(0, min(min_activity_count - 1, len(alist) - 1))
    threshold = alist[i][1]
    i = i + 1
    while i < len(alist):
        value = alist[i][1]
        if value > threshold * decreasing_factor:
            threshold = value
        if i >= max_activity_count:
            break
        i = i + 1
    return threshold