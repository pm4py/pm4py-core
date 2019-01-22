from sklearn import tree

DEFAULT_MAX_REC_DEPTH = 7


def mine(data, target, max_depth=DEFAULT_MAX_REC_DEPTH):
    """
    Mine a decision tree

    Parameters
    ------------
    data
        Data from which the decision tree shall be learned
    target
        Target classes
    max_depth
        Maximum depth of the recursion tree

    Returns
    ------------
    clf
        Decision tree
    """
    clf = tree.DecisionTreeClassifier(max_depth=max_depth)
    clf = clf.fit(data, target)

    return clf
