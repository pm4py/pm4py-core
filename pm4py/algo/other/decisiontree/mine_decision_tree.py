from sklearn import tree

def mine(data, target):
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(data, target)
    return clf