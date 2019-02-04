from pm4py.algo.enhancement.sna.versions import handover, working_together, subcontracting, jointactivities
from pm4py.objects.conversion.log import factory as conv_factory

HANDOVER = "handover"
WORKING_TOGETHER = "working_together"
SUBCONTRACTING = "subcontracting"
JOINTACTIVITIES = "jointactivities"

VERSIONS_LOG = {HANDOVER: handover.apply, WORKING_TOGETHER: working_together.apply,
                SUBCONTRACTING: subcontracting.apply, JOINTACTIVITIES: jointactivities.apply}


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
            handover, working_together

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
