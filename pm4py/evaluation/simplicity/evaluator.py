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
from pm4py.evaluation.simplicity.variants import arc_degree
from enum import Enum
from pm4py.util import exec_utils
import deprecation
from pm4py.meta import VERSION
import warnings


class Variants(Enum):
    SIMPLICITY_ARC_DEGREE = arc_degree


SIMPLICITY_ARC_DEGREE = Variants.SIMPLICITY_ARC_DEGREE

VERSIONS = {SIMPLICITY_ARC_DEGREE}


@deprecation.deprecated(deprecated_in="2.2.5", removed_in="3.0",
                        current_version=VERSION,
                        details="Use the pm4py.algo.evaluation.simplicity package")
def apply(petri_net, parameters=None, variant=SIMPLICITY_ARC_DEGREE):
    warnings.warn("Use the pm4py.algo.evaluation.simplicity package")
    return exec_utils.get_variant(variant).apply(petri_net, parameters=parameters)
