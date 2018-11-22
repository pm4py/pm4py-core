from sklearn import tree


def mine(data, target):
    """
    Mine a decision tree

    Parameters
    ------------
    data
        Data from which the decision tree shall be learned
    target
        Target classes

    Returns
    ------------
    clf
        Decision tree
    """
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(data, target)
    return clf