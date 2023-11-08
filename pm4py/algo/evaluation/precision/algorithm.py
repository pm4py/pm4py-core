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
from pm4py.algo.evaluation.precision.variants import etconformance_token
from pm4py.algo.evaluation.precision.variants import align_etconformance
from pm4py.objects.petri_net.utils.check_soundness import check_easy_soundness_net_in_fin_marking
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
import pandas as pd


class Variants(Enum):
    ETCONFORMANCE_TOKEN = etconformance_token
    ALIGN_ETCONFORMANCE = align_etconformance


ETCONFORMANCE_TOKEN = Variants.ETCONFORMANCE_TOKEN
ALIGN_ETCONFORMANCE = Variants.ALIGN_ETCONFORMANCE

VERSIONS = {ETCONFORMANCE_TOKEN, ALIGN_ETCONFORMANCE}


def apply(log: Union[EventLog, EventStream, pd.DataFrame], net: PetriNet, marking: Marking, final_marking: Marking, parameters: Optional[Dict[Any, Any]] = None, variant=None) -> float:
    """
    Method to apply ET Conformance

    Parameters
    -----------
    log
        Trace log
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm, including:
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Activity key
    variant
        Variant of the algorithm that should be applied:
            - Variants.ETCONFORMANCE_TOKEN
            - Variants.ALIGN_ETCONFORMANCE
    """
    if parameters is None:
        parameters = {}

    # execute the following part of code when the variant is not specified by the user
    if variant is None:
        if not (check_easy_soundness_net_in_fin_marking(
                net,
                marking,
                final_marking)):
            # in the case the net is not a easy sound workflow net, we must apply token-based replay
            variant = ETCONFORMANCE_TOKEN
        else:
            # otherwise, use the align-etconformance approach (safer, in the case the model contains duplicates)
            variant = ALIGN_ETCONFORMANCE

    return exec_utils.get_variant(variant).apply(log, net, marking,
                             final_marking, parameters=parameters)
