from pm4py.algo.filtering.tracelog.variants import variants_filter


def filter_topvariants_soundmodel(log, parameters=None):
    if parameters is None:
        parameters = {}

    discovery_algorithm = parameters["discovery_algorithm"] if "discovery_algorithm" in parameters else "alphaclassic"
    max_no_variants = parameters["max_no_variants"] if "max_no_variants" in parameters else 10