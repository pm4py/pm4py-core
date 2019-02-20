from pm4py.algo.enhancement.sna.versions.log import handover as log_handover, jointactivities as log_jointactivities, subcontracting as log_subcontracting, working_together as log_workingtogether
from pm4py.algo.enhancement.sna.versions.pandas import handover as pd_handover, subcontracting as pd_subcontracting, working_together as pd_workingtogether, jointactivities as pd_jointactivities
from pm4py.objects.conversion.log import factory as conv_factory
import pandas

HANDOVER = "handover"
WORKING_TOGETHER = "working_together"
SUBCONTRACTING = "subcontracting"
JOINTACTIVITIES = "jointactivities"

VERSIONS_LOG = {HANDOVER: log_handover.apply, WORKING_TOGETHER: log_workingtogether.apply,
                SUBCONTRACTING: log_subcontracting.apply, JOINTACTIVITIES: log_jointactivities.apply}
VERSIONS_PANDAS = {HANDOVER: pd_handover.apply, WORKING_TOGETHER: pd_workingtogether.apply,
                   SUBCONTRACTING: pd_subcontracting.apply, JOINTACTIVITIES: pd_jointactivities.apply}


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
    if variant in VERSIONS_PANDAS and type(log) is pandas.DataFrame:
        return VERSIONS_PANDAS[variant](log, parameters=parameters)
    if variant in VERSIONS_LOG:
        log = conv_factory.apply(log, parameters=parameters)
        return VERSIONS_LOG[variant](log, parameters=parameters)

    raise Exception("metric not implemented yet")
