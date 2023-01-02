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

from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Union
from pm4py.utils import __event_log_deprecation_warning
from pm4py.objects.conversion.log import converter as log_converter


def anonymize_differential_privacy(log: Union[EventLog, EventStream, pd.DataFrame], epsilon: float = 0.5, k: int = 30, p: int = 4) -> EventLog:
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

    :param log: log object (event log / event stream / Pandas dataframe)
    :param epsilon: the strength of the differential privacy guarantee. The smaller the value of epsilon, the stronger the privacy guarantee that is provided.
    :param k: the maximal length of considered traces in the prefix tree.
    :param p: the pruning parameter, which denotes the minimum count a prefix has to have in order to not be discarded. The  dependent exponential runtime of the algorithms is mitigated by the pruning parameter.
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        event_log = pm4py.read_xes("running-example.xes")
        diff_priv_event_log = pm4py.anonymize_differential_privacy(event_log, epsilon=0.5, k=30, p=1)
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    from pm4py.algo.anonymization.trace_variant_query import algorithm as trace_variant_query
    sacofa_result = trace_variant_query.apply(log=log, variant=trace_variant_query.Variants.SACOFA, parameters={"epsilon": epsilon, "k": k, "p": p})

    from pm4py.algo.anonymization.pripel.variants import pripel
    log = pripel.apply(log, sacofa_result, epsilon=epsilon)

    return log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)
