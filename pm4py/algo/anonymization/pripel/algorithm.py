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

from pm4py.algo.anonymization.pripel.variants import pripel
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils


class Variants(Enum):
    PRIPEL = pripel


DEFAULT_VARIANT = Variants.PRIPEL

VERSIONS = {Variants.PRIPEL}


def apply(log: Union[EventLog, pd.DataFrame], trace_variant_query: Union[EventLog, pd.DataFrame], epsilon: float,
          variant=DEFAULT_VARIANT,
          parameters: Optional[Dict[Any, Any]] = None) -> EventLog:
    """
    PRIPEL (Privacy-preserving event log publishing with contextual information) is a framework to publish event logs
    that fulfill differential privacy. PRIPEL ensures privacy on the level of individual cases instead of the complete
    log. This way, contextual information as well as the long tail process behaviour are preserved, which enables the
    application of a rich set of process analysis techniques.

    PRIPEL is described in:
    Fahrenkrog-Petersen, S.A., van der Aa, H., Weidlich, M. (2020). PRIPEL: Privacy-Preserving Event Log Publishing
    Including Contextual Information. In: Fahland, D., Ghidini, C., Becker, J., Dumas, M. (eds) Business Process
    Management. BPM 2020. Lecture Notes in Computer Science(), vol 12168. Springer, Cham.
    https://doi.org/10.1007/978-3-030-58666-9_7


    Parameters
    -------------
    log
        Event log
    trace_variant_query
        An anonymized trace variant distribution as an EventLog
    epsilon
        Strength of the differential privacy guarantee
    variant
        - Variants.PRIPEL
    parameters
        Parameters of the algorithm, including:
            -Parameters.BLOCKLIST -> Some event logs contain attributes that are equivalent to a case id. For privacy reasons, such attributes must be deleted from the anonymized log. We handle such attributes with this set.
    Returns
    ------------
    anonymised_log
        Anonymised event log
    """

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    trace_variant_query = log_converter.apply(trace_variant_query, variant=log_converter.Variants.TO_EVENT_LOG)

    return exec_utils.get_variant(variant).apply(log, trace_variant_query, epsilon, parameters=parameters)
