from pm4py.algo.discovery.simple.filtering.log.versions import filter_topvariants_soundmodel

TOPVARIANTS_SOUNDMODEL = "topvariants_soundmodel"

VERSIONS = {TOPVARIANTS_SOUNDMODEL: filter_topvariants_soundmodel.apply}


def apply(log, parameters=None, variant=TOPVARIANTS_SOUNDMODEL):
    """
    Apply a filtering algorithm in a simple way in order to provide
    a simple visualization

    Parameters
    -----------
    log
        Trace log
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm, including: topvariants_soundmodel

    Returns
    -----------
    filtered_log
        Filtered log
    """
    return VERSIONS[variant](log, parameters=parameters)
