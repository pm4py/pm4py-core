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
from pm4py.algo.enhancement.sna.variants.log import handover as log_handover, jointactivities as log_jointactivities, \
    subcontracting as log_subcontracting, working_together as log_workingtogether
from pm4py.algo.enhancement.sna.variants.pandas import handover as pd_handover, subcontracting as pd_subcontracting, \
    working_together as pd_workingtogether, jointactivities as pd_jointactivities
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.algo.enhancement.sna.parameters import Parameters
from pm4py.util import exec_utils
from enum import Enum
import numpy as np


class Variants(Enum):
    HANDOVER_LOG = log_handover
    WORKING_TOGETHER_LOG = log_workingtogether
    SUBCONTRACTING_LOG = log_subcontracting
    JOINTACTIVITIES_LOG = log_jointactivities
    HANDOVER_PANDAS = pd_handover
    WORKING_TOGETHER_PANDAS = pd_workingtogether
    SUBCONTRACTING_PANDAS = pd_subcontracting
    JOINTACTIVITIES_PANDAS = pd_jointactivities


def apply(log, parameters=None, variant=Variants.HANDOVER_LOG):
    """
    Calculates a SNA metric

    Parameters
    ------------
    log
        Log
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm to apply. Possible values:
            - Variants.HANDOVER_LOG
            - Variants.WORKING_TOGETHER_LOG
            - Variants.SUBCONTRACTING_LOG
            - Variants.JOINTACTIVITIES_LOG
            - Variants.HANDOVER_PANDAS
            - Variants.WORKING_TOGETHER_PANDAS
            - Variants.SUBCONTRACTING_PANDAS
            - Variants.JOINTACTIVITIES_PANDAS

    Returns
    -----------
    tuple
        Tuple containing the metric matrix and the resources list
    """
    if parameters is None:
        parameters = {}

    enable_metric_normalization = exec_utils.get_param_value(Parameters.METRIC_NORMALIZATION, parameters, False)

    if variant in [Variants.HANDOVER_LOG, Variants.WORKING_TOGETHER_LOG, Variants.JOINTACTIVITIES_LOG,
                   Variants.SUBCONTRACTING_LOG]:
        log = log_conversion.apply(log, parameters=parameters)
    sna = exec_utils.get_variant(variant).apply(log, parameters=parameters)
    abs_max = np.max(np.abs(sna[0]))
    if enable_metric_normalization and abs_max > 0:
        sna[0] = sna[0] / abs_max
    return sna
