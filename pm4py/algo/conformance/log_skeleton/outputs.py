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

import warnings
warnings.warn("pm4py.algo.conformance.log_skeleton.outputs is deprecated.")


class Outputs(Enum):
    DEVIATIONS = "deviations"
    NO_DEV_TOTAL = "no_dev_total"
    NO_CONSTR_TOTAL = "no_constr_total"
    DEV_FITNESS = "dev_fitness"
    IS_FIT = "is_fit"
