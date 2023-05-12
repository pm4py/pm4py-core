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
from enum import Enum
from typing import Optional, Dict, Any, Union

import pandas as pd

from pm4py.algo.anonymization.trace_variant_query.variants import laplace, sacofa  # , sapa
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils


class Variants(Enum):
    LAPLACE = laplace
    SACOFA = sacofa


DEFAULT_VARIANT = Variants.SACOFA


def apply(log: Union[EventLog, pd.DataFrame], variant=DEFAULT_VARIANT,
          parameters: Optional[Dict[Any, Any]] = None) -> EventLog:
    """
    Applies a trace variant query to an event log. A trace variant query returns an event log that
    captures trace variants and their frequencies in a differentially private manner, in other words it returns an
    anonymized trace variant distribution. Such a step is essential, given that even the publication of activity
    sequences from an event log, i.e., with all attribute values and timestamps removed, can be sufficient to link the
    identity of individuals to infrequent activity sequences.

    Variant Laplace is described in:
    Mannhardt, F., Koschmider, A., Baracaldo, N. et al. Privacy-Preserving Process Mining. Bus Inf Syst Eng 61,
    595–614 (2019). https://doi.org/10.1007/s12599-019-00613-3

    Variant SaCoFa is described in:
    S. A. Fahrenkog-Petersen, M. Kabierski, F. Rösel, H. van der Aa and M. Weidlich, "SaCoFa: Semantics-aware
    Control-flow Anonymization for Process Mining," 2021 3rd International Conference on Process Mining (ICPM), 2021,
    pp. 72-79, doi: 10.1109/ICPM53251.2021.9576857.

    Variant DF-Laplace:

    Parameters
    -------------
    log
        Log
    variant
        Variant of the algorithm to apply, possible values:
            -Variants.LAPLACE
            -Variants.SACOFA
    parameters
        Parameters of the algorithm, including:
            -Parameters.EPSILON -> Strength of the differential privacy guarantee
            -Parameters.K -> Maximum prefix length of considered traces for the trace-variant-query
            -Parameters.P -> Pruning parameter of the trace-variant-query. Of a noisy trace variant, at least P traces
                            must appear. Otherwise, the trace variant and its traces won't be part of the result of the
                            trace variant query.
    Returns
    --------------
    anonymized_trace_variant_distribution
        An anonymized trace variant distribution as an EventLog
    """
    if parameters is None:
        parameters = {}
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)
    tvq_log = exec_utils.get_variant(variant).apply(log, parameters=parameters)
    if (len(tvq_log) == 0):
        raise ValueError(
            "The pruning parameter p is probably too high. The result of the trace variant query is empty. Of a noisy trace "
            "variant, at least p traces must appear. Otherwise, the trace variant and its traces won't be part of the "
            "result of the trace variant query.")
    tvq_log = log_converter.apply(tvq_log, variant=log_converter.Variants.TO_DATA_FRAME)
    return tvq_log
