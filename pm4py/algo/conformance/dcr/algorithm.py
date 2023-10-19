import pm4py
from pm4py.objects.log.obj import EventLog
import pandas as pd
from pm4py.objects.dcr.obj import DCR_Graph
from pm4py.algo.conformance.dcr.variants import classic
from enum import Enum
from pm4py.util import exec_utils
from typing import Union, Any, Dict, Tuple, List, Optional


class Variants(Enum):
    CLASSIC = classic


CLASSIC = Variants.CLASSIC
VERSIONS = {CLASSIC}


def apply(log: Union[pd.DataFrame, EventLog], dcr: DCR_Graph, variant=CLASSIC,
          parameters=None) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Applies conformance checking against a DECLARE model.

    Parameters
    --------------
    log
        Event log / Pandas dataframe
    dcr
        DCR Graph
    variant
        Variant to be used:
        - Variants.CLASSIC
     parameters
        Parameters
        - Parameters.ACTIVITY_KEY
        - Parameters.CASE_ID_KEY
        - PARAMETERS.ROLE_KEY

    Returns
    -------------
    traces
        List containing for every case a dictionary with different keys:
        - no_constr_total => the total number of constraints of the DECLARE model
        - deviations => a list of deviations
        - no_dev_total => the total number of deviations
        - dev_fitness => the fitness (1 - no_dev_total / no_constr_total)
        - is_fit => True if the case is perfectly fit
    """

    if parameters is None:
        parameters = {}
    # run apply function to return template with fulfilled and violated activities
    return exec_utils.get_variant(variant).apply(log, dcr, parameters)


def get_diagnostics_dataframe(log, conf_result, variant=Variants.CLASSIC, parameters=None) -> pd.DataFrame:
    """
    Gets the diagnostics dataframe from a log and the results
    of DECLARE-based conformance checking

    Parameters
    --------------
    log
        Event log
    conf_result
        Results of conformance checking
    variant
        Variant to be used:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    --------------
    diagn_dataframe
        Diagnostics dataframe
    """
    if parameters is None:
        parameters = {}
    return exec_utils.get_variant(variant).get_diagnostics_dataframe(log, conf_result, parameters)
