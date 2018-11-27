from pm4py.algo.other.simple.model.tracelog.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(log, parameters=None, variant=CLASSIC):
    return VERSIONS[variant](log, parameters=parameters)