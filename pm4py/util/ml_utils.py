import importlib.util


def DecisionTreeClassifier(*args, **kwargs):
    from sklearn.tree import DecisionTreeClassifier

    return DecisionTreeClassifier(*args, **kwargs)


def AffinityPropagation(*args, **kwargs):
    from sklearn.cluster import AffinityPropagation

    return AffinityPropagation(*args, **kwargs)


def KMeans(*args, **kwargs):
    from sklearn.cluster import KMeans

    return KMeans(*args, **kwargs)


def KNeighborsRegressor(*args, **kwargs):
    from sklearn.neighbors import KNeighborsRegressor

    return KNeighborsRegressor(*args, **kwargs)


def LocallyLinearEmbedding(*args, **kwargs):
    from sklearn.manifold import LocallyLinearEmbedding

    return LocallyLinearEmbedding(*args, **kwargs)
