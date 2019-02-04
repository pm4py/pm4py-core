from pm4py.algo.enhancement.sna.versions import handover
from pm4py.objects.conversion.log import factory as conv_factory

HANDOVER = "handover"

VERSIONS_LOG = {HANDOVER: handover.apply}


def apply(log, parameters=None, variant=HANDOVER):
    """
    Calculates a SNA metric

    Parameters
    ------------
    log
        Log
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm to apply. Possible values:
            handover

    Returns
    -----------
    tuple
        Tuple containing the metric matrix and the resources list
    """
    if parameters is None:
        parameters = {}

    if variant in VERSIONS_LOG:
        log = conv_factory.apply(log, parameters=parameters)
        return VERSIONS_LOG[variant](log, parameters=parameters)

    raise Exception("metric not implemented yet")
