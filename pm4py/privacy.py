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

from pm4py.objects.log.obj import EventLog
import pandas as pd
from typing import Union


def anonymize_differential_privacy(log: Union[EventLog, pd.DataFrame], epsilon: float = 1.0, k: int = 10, p: int = 20) -> pd.DataFrame:
    """
    Protect event logs with differential privacy. Differential privacy is a guarantee that bounds the impact the data of one individual has on a query result.

    Control-flow information is anonymized with SaCoFa. This algorithm inserts noise into a trace-variant count, through the step-wise construction of a prefix tree.

    Contextual-information, like timestamps or resources, is anonymized with PRIPEL. This technique enriches a control-flow anonymized event log with contextual information from the original log, while still achieving differential privacy.
    PRIPEL anonymizes each event's timestamp and other attributes, that are stored as strings, integers, floats, or booleans.

    Please install diffprivlib https://diffprivlib.readthedocs.io/en/latest/ (pip install diffprivlib==0.5.2) to run our algorithm.


    SaCoFa is described in:
    S. A. Fahrenkog-Petersen, M. Kabierski, F. Rösel, H. van der Aa and M. Weidlich, "SaCoFa: Semantics-aware
    Control-flow Anonymization for Process Mining," 2021 3rd International Conference on Process Mining (ICPM), 2021,
    pp. 72-79. https://doi.org/10.48550/arXiv.2109.08501

    PRIPEL is described in:
    Fahrenkrog-Petersen, S.A., van der Aa, H., Weidlich, M. (2020). PRIPEL: Privacy-Preserving Event Log Publishing
    Including Contextual Information. In: Fahland, D., Ghidini, C., Becker, J., Dumas, M. (eds) Business Process
    Management. BPM 2020. Lecture Notes in Computer Science, vol 12168. Springer, Cham.
    https://doi.org/10.1007/978-3-030-58666-9_7


    :param log: event log / Pandas dataframe
    :param epsilon: the strength of the differential privacy guarantee. The smaller the value of epsilon, the stronger the privacy guarantee that is provided.
    :param k: the maximal length of considered traces in the prefix tree. We recommend setting k, that roughly 80% of all traces from the original event log are covered.
    :param p: the pruning parameter, which denotes the minimum count a prefix has to have in order to not be discarded. The dependent exponential runtime of the algorithms is mitigated by the pruning parameter.
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        event_log = pm4py.read_xes("running-example.xes")
        anonymized_event_log = pm4py.anonymize_differential_privacy(event_log, epsilon=1.0, k=10, p=20)
    """

    from pm4py.algo.anonymization.trace_variant_query import algorithm as trace_variant_query
    sacofa_result = trace_variant_query.apply(log=log, variant=trace_variant_query.Variants.SACOFA, parameters={"epsilon": epsilon, "k": k, "p": p})

    from pm4py.algo.anonymization.pripel import algorithm as pripel
    anonymized_log = pripel.apply(log, sacofa_result, epsilon=epsilon)

    return anonymized_log
