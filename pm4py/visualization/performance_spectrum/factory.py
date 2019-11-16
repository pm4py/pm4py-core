from pm4py.visualization.performance_spectrum.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}

def apply(ps, variant="classic", parameters=None):
    return VERSIONS[variant](ps, parameters=parameters)

