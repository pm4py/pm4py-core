from pm4py.visualization.intervaltree.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(tree_distr_points, variant="classic", parameters=None):
    if parameters is None:
        parameters = {}

    return VERSIONS[CLASSIC](tree_distr_points, parameters=parameters)
