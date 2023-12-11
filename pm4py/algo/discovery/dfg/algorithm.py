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
from pm4py.algo.discovery.dfg.variants import native, performance, freq_triples, case_attributes, clean
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.util import xes_constants as xes_util
from pm4py.util import exec_utils
from pm4py.util import constants, pandas_utils
from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


class Variants(Enum):
    NATIVE = native
    FREQUENCY = native
    PERFORMANCE = performance
    FREQUENCY_GREEDY = native
    PERFORMANCE_GREEDY = performance
    FREQ_TRIPLES = freq_triples
    CASE_ATTRIBUTES = case_attributes
    CLEAN = clean # 'novel' replacement for native


DFG_NATIVE = Variants.NATIVE
DFG_FREQUENCY = Variants.FREQUENCY
DFG_PERFORMANCE = Variants.PERFORMANCE
DFG_FREQUENCY_GREEDY = Variants.FREQUENCY_GREEDY
DFG_PERFORMANCE_GREEDY = Variants.PERFORMANCE_GREEDY
FREQ_TRIPLES = Variants.FREQ_TRIPLES
DFG_CLEAN = Variants.CLEAN

DEFAULT_VARIANT = Variants.NATIVE

VERSIONS = {DFG_NATIVE, DFG_FREQUENCY, DFG_PERFORMANCE, DFG_FREQUENCY_GREEDY, DFG_PERFORMANCE_GREEDY, FREQ_TRIPLES}


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> Dict[Tuple[str, str], float]:
    """
    Calculates DFG graph (frequency or performance) starting from a log

    Parameters
    ----------
    log
        Log
    parameters
        Possible parameters passed to the algorithms:
            Parameters.AGGREGATION_MEASURE -> performance aggregation measure (min, max, mean, median)
            Parameters.ACTIVITY_KEY -> Attribute to use as activity
            Parameters.TIMESTAMP_KEY -> Attribute to use as timestamp
    variant
        Variant of the algorithm to use, possible values:
            - Variants.NATIVE
            - Variants.FREQUENCY
            - Variants.FREQUENCY_GREEDY
            - Variants.PERFORMANCE
            - Variants.PERFORMANCE_GREEDY
            - Variants.FREQ_TRIPLES

    Returns
    -------
    dfg
        DFG graph
    """
    if variant == Variants.CLEAN and pandas_utils.check_is_pandas_dataframe(log):
        return clean.apply(log, parameters)
    elif variant is None:
        variant = Variants.NATIVE
    
    if parameters is None:
        parameters = {}
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, None)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, pmutil.constants.CASE_CONCEPT_NAME)

    if pandas_utils.check_is_pandas_dataframe(log) and not variant == Variants.FREQ_TRIPLES:
        dfg_frequency, dfg_performance = df_statistics.get_dfg_graph(log, measure="both",
                                                                     activity_key=activity_key,
                                                                     timestamp_key=timestamp_key,
                                                                     case_id_glue=case_id_glue,
                                                                     start_timestamp_key=start_timestamp_key)
        if variant in [Variants.PERFORMANCE, Variants.PERFORMANCE_GREEDY]:
            return dfg_performance
        else:
            return dfg_frequency

    return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG), parameters=parameters)
