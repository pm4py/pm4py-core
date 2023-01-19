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

from pm4py.algo.anonymization.pripel.util.AttributeAnonymizer import AttributeAnonymizer
from pm4py.algo.anonymization.pripel.util.TraceMatcher import TraceMatcher
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils


class Parameters(Enum):
    BLOCKLIST = "blocklist"


def apply_pripel(log, tv_query_log, epsilon, blocklist):
    if (len(tv_query_log) == 0):
        raise ValueError(
            "Pruning parameter k is too high. The result of the trace variant query is empty. At least k traces must appear "
            "in a noisy variant count to be part of the result of the query.")
    for trace in log:
        delTraceAttributes = set()
        for attribute in trace.attributes.keys():
            if pd.isnull(trace.attributes[attribute]):
                delTraceAttributes.add(attribute)
            if blocklist is not None:
                if attribute in blocklist:
                    delTraceAttributes.add(attribute)
        for attribute in delTraceAttributes:
            trace.attributes.pop(attribute)
        for event in trace:
            delAttributes = set()
            for attribute in event.keys():
                if blocklist is not None:
                    if attribute in blocklist:
                        delAttributes.add(attribute)
                if pd.isnull(event[attribute]):
                    delAttributes.add(attribute)
                if not isinstance(event[attribute], (float, str, int, bool)) and attribute != "time:timestamp":
                    delAttributes.add(attribute)
            for attribute in delAttributes:
                event._dict.pop(attribute)

    traceMatcher = TraceMatcher(tv_query_log, log)
    matchedLog = traceMatcher.matchQueryToLog()

    distributionOfAttributes = traceMatcher.getAttributeDistribution()
    occurredTimestamps, occurredTimestampDifferences = traceMatcher.getTimeStampData()

    attributeAnonymizer = AttributeAnonymizer()
    anonymizedLog = attributeAnonymizer.anonymize(matchedLog, distributionOfAttributes, epsilon,
                                                  occurredTimestampDifferences,
                                                  occurredTimestamps)
    for i in range(len(anonymizedLog)):
        anonymizedLog[i].attributes['concept:name'] = str(i)
        anonymizedLog[i].attributes.pop('variant', None)

    anonymizedLog = log_converter.apply(anonymizedLog, variant=log_converter.Variants.TO_DATA_FRAME)

    return anonymizedLog


def apply(log: Union[EventLog, pd.DataFrame], traceVariantQuery: Union[EventLog, pd.DataFrame], epsilon: float,
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
    traceVariantQuery
        An anonymized trace variant distribution as an EventLog
    epsilon
        Strength of the differential privacy guarantee
    parameters
        Parameters of the algorithm, including:
            -Parameters.BLOCKLIST -> Some event logs contain attributes that are equivalent to a case id. For privacy
            reasons, such attributes must be deleted from the anonymized log. We handle such attributes with this list.
    Returns
    ------------
    anonymised_log
        Anonymised event log
    """

    if parameters is None:
        parameters = {}

    blocklist = exec_utils.get_param_value(Parameters.BLOCKLIST, parameters, None)

    return apply_pripel(log, traceVariantQuery, epsilon, blocklist)
