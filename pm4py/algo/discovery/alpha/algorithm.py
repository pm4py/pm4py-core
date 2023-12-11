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
from pm4py import util as pmutil
from pm4py.algo.discovery.alpha import variants
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.statistics.start_activities.pandas import get as start_activities_get
from pm4py.statistics.end_activities.pandas import get as end_activities_get
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.util import exec_utils
from pm4py.util import xes_constants as xes_util
from pm4py.util import constants, pandas_utils
from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from pm4py.objects.petri_net.obj import PetriNet, Marking


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


class Variants(Enum):
    ALPHA_VERSION_CLASSIC = variants.classic
    ALPHA_VERSION_PLUS = variants.plus


ALPHA_VERSION_CLASSIC = Variants.ALPHA_VERSION_CLASSIC
ALPHA_VERSION_PLUS = Variants.ALPHA_VERSION_PLUS
DEFAULT_VARIANT = ALPHA_VERSION_CLASSIC
VERSIONS = {Variants.ALPHA_VERSION_CLASSIC, Variants.ALPHA_VERSION_PLUS}


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Union[str, Parameters], Any]] = None, variant=DEFAULT_VARIANT) -> Tuple[PetriNet, Marking, Marking]:
    """
    Apply the Alpha Miner on top of a log

    Parameters
    -----------
    log
        Log
    variant
        Variant of the algorithm to use:
            - Variants.ALPHA_VERSION_CLASSIC
            - Variants.ALPHA_VERSION_PLUS
    parameters
        Possible parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Name of the attribute that contains the activity

    Returns
    -----------
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, pmutil.constants.CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     None)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)

    if pandas_utils.check_is_pandas_dataframe(log) and variant == ALPHA_VERSION_CLASSIC:
        dfg = df_statistics.get_dfg_graph(log, case_id_glue=case_id_glue,
                                          activity_key=activity_key,
                                          timestamp_key=timestamp_key, start_timestamp_key=start_timestamp_key)
        start_activities = start_activities_get.get_start_activities(log, parameters=parameters)
        end_activities = end_activities_get.get_end_activities(log, parameters=parameters)
        return exec_utils.get_variant(variant).apply_dfg_sa_ea(dfg, start_activities, end_activities, parameters=parameters)

    return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG),
                                                 parameters)


def apply_dfg(dfg: Dict[Tuple[str, str], int], parameters: Optional[Dict[Union[str, Parameters], Any]] = None, variant=ALPHA_VERSION_CLASSIC) -> Tuple[PetriNet, Marking, Marking]:
    """
    Apply Alpha Miner directly on top of a DFG graph

    Parameters
    -----------
    dfg
        Directly-Follows graph
    variant
        Variant of the algorithm to use (classic)
    parameters
        Possible parameters of the algorithm, including:
            activity key -> Name of the attribute that contains the activity

    Returns
    -----------
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}
    return exec_utils.get_variant(variant).apply_dfg(dfg, parameters)
