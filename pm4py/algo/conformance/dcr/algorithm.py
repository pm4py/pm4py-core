import pm4py
from pm4py.objects.log.obj import EventLog
import pandas as pd
from pm4py.algo.conformance.dcr.variants import classic
from enum import Enum
from pm4py.util import exec_utils
from typing import Union, Any, Dict, Tuple, List, Optional
from pm4py.util import constants


class Variants(Enum):
    CLASSIC = classic


def apply(log: Union[pd.DataFrame, EventLog], G, variant=Variants.CLASSIC,
          parameters: Optional[Dict[Union[Any, Any], Any]] = None) -> List[Dict[str, Any]]:
    """
    Applies rule based conformance checking against a DCR graph and an event log.

    Parameters
    ----------
    log
        Event log / Pandas dataframe
    G
        DCR Graph

    variant
        Variant to be used:
        - Variants.CLASSIC

    parameters
        Variant-specific parameters

    Returns
    ----------
    conf_res
        List containing dictionaries with the following keys and values:
        - no_constr_total: the total number of constraints of the DCR Graphs
        - deviations: the list of deviations
        - no_dev_total: the total number of deviations
        - dev_fitness: the fitness (1 - no_dev_total / no_constr_total),
        - is_fit: True if the case is perfectly fit
    """

    # run apply function to return template with fulfilled and violated activities
    return exec_utils.get_variant(variant).apply(log, G, parameters)


def get_diagnostics_dataframe(log: Union[EventLog, pd.DataFrame], conf_result: List[Dict[str, Any]], variant=Variants.CLASSIC, parameters=None) -> pd.DataFrame:
    """
    Gets the diagnostics dataframe from a log and the conformance results

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
    return exec_utils.get_variant(variant).get_diagnostics_dataframe(log, conf_result, parameters)
