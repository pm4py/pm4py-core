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
from pm4py.evaluation.generalization.variants import token_based
from pm4py.objects.conversion.log import converter as log_conversion
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    GENERALIZATION_TOKEN = token_based


GENERALIZATION_TOKEN = Variants.GENERALIZATION_TOKEN
VERSIONS = {GENERALIZATION_TOKEN}


def apply(log, petri_net, initial_marking, final_marking, parameters=None, variant=GENERALIZATION_TOKEN):
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG),
                                                 petri_net,
                                                 initial_marking, final_marking, parameters=parameters)
