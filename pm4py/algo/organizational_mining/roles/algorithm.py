from pm4py.algo.organizational_mining.roles.variants import pandas
from pm4py.algo.organizational_mining.roles.variants import log
from pm4py.util import exec_utils
from enum import Enum
from typing import Optional, Dict, Any, Union, List
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Variants(Enum):
    LOG = log
    PANDAS = pandas


def apply(log: Union[EventLog, EventStream, pd.DataFrame], variant=None, parameters: Optional[Dict[Any, Any]] = None) -> List[Any]:
    """
    Gets the roles (group of different activities done by similar resources)
    out of the log.

    The roles detection is introduced by
    Burattin, Andrea, Alessandro Sperduti, and Marco Veluscek. "Business models enhancement through discovery of roles." 2013 IEEE Symposium on Computational Intelligence and Data Mining (CIDM). IEEE, 2013.


    Parameters
    -------------
    log
        Log object (also Pandas dataframe)
    variant
        Variant of the algorithm to apply. Possible values:
            - Variants.LOG
            - Variants.PANDAS
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    roles
        List of different roles inside the log, including:
        roles_threshold_parameter => threshold to use with the algorithm
    """
    if parameters is None:
        parameters = {}

    if variant is None:
        if type(log) is pd.DataFrame:
            variant = Variants.PANDAS

        if variant is None:
            variant = Variants.LOG

    return exec_utils.get_variant(variant).apply(log, parameters=parameters)
