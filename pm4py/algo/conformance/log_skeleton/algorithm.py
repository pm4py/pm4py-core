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
from pm4py.algo.conformance.log_skeleton.variants import classic
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, List, Set
from pm4py.objects.log.obj import EventLog, Trace
import pandas as pd


class Variants(Enum):
    CLASSIC = classic


CLASSIC = Variants.CLASSIC
DEFAULT_VARIANT = Variants.CLASSIC


def apply(obj: Union[EventLog, Trace, pd.DataFrame], model: Dict[str, Any], variant=DEFAULT_VARIANT, parameters: Optional[Dict[Any, Any]] = None) -> List[Set[Any]]:
    """
    Apply log-skeleton based conformance checking given an event log/trace
    and a log-skeleton model

    Parameters
    --------------
    obj
        Object (event log/trace)
    model
        Log-skeleton model
    variant
        Variant of the algorithm, possible values: Variants.CLASSIC
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY
        - Parameters.CONSIDERED_CONSTRAINTS, among: equivalence, always_after, always_before, never_together, directly_follows, activ_freq

    Returns
    --------------
    aligned_traces
        Conformance checking results for each trace:
        - Outputs.IS_FIT => boolean that tells if the trace is perfectly fit according to the model
        - Outputs.DEV_FITNESS => deviation based fitness (between 0 and 1; the more the trace is near to 1 the more fit is)
        - Outputs.DEVIATIONS => list of deviations in the model
    """
    if parameters is None:
        parameters = {}

    if type(obj) is Trace:
        return exec_utils.get_variant(variant).apply_trace(obj, model, parameters=parameters)
    else:
        return exec_utils.get_variant(variant).apply_log(obj, model, parameters=parameters)


def apply_from_variants_list(var_list: List[List[str]], model: Dict[str, Any], variant=DEFAULT_VARIANT, parameters: Optional[Dict[Any, Any]] = None) -> List[Set[Any]]:
    """
    Performs conformance checking using the log skeleton,
    applying it from a list of variants

    Parameters
    --------------
    var_list
        List of variants
    model
        Log skeleton model
    variant
        Variant of the algorithm, possible values: Variants.CLASSIC
    parameters
        Parameters

    Returns
    --------------
    conformance_dictio
        Dictionary containing, for each variant, the result
        of log skeleton checking
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply_from_variants_list(var_list, model, parameters=parameters)


def get_diagnostics_dataframe(log: EventLog, conf_result: List[Set[Any]], variant=DEFAULT_VARIANT, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Gets the diagnostics dataframe from a log and the results
    of log skeleton-based conformance checking

    Parameters
    --------------
    log
        Event log
    conf_result
        Results of conformance checking

    Returns
    --------------
    diagn_dataframe
        Diagnostics dataframe
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).get_diagnostics_dataframe(log, conf_result, parameters=parameters)
