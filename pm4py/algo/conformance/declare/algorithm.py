'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''

from pm4py.util import exec_utils
from enum import Enum
from pm4py.algo.conformance.declare.variants import classic
from pm4py.objects.log.obj import EventLog
import pandas as pd
from typing import Union, Dict, Optional, Any, List


class Variants(Enum):
    CLASSIC = classic


def apply(log: Union[EventLog, pd.DataFrame], model: Dict[str, Dict[Any, Dict[str, int]]], variant=Variants.CLASSIC,
          parameters: Optional[Dict[Any, Any]] = None) -> List[Dict[str, Any]]:
    """
    Applies conformance checking against a DECLARE model.

    Parameters
    --------------
    log
        Event log / Pandas dataframe
    model
        DECLARE model
    variant
        Variant to be used:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    -------------
    lst_conf_res
        List containing for every case a dictionary with different keys:
        - no_constr_total => the total number of constraints of the DECLARE model
        - deviations => a list of deviations
        - no_dev_total => the total number of deviations
        - dev_fitness => the fitness (1 - no_dev_total / no_constr_total)
        - is_fit => True if the case is perfectly fit
    """
    return exec_utils.get_variant(variant).apply(log, model, parameters)


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
    return exec_utils.get_variant(variant).get_diagnostics_dataframe(log, conf_result, parameters)
