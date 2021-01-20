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
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY, PARAMETER_CONSTANT_CASEID_KEY


class Parameters(Enum):
    # parameter for the noise threshold
    NOISE_THRESHOLD = "noise_threshold"
    # considered constraints in conformance checking among: equivalence, always_after, always_before, never_together, directly_follows, activ_freq
    CONSIDERED_CONSTRAINTS = "considered_constraints"
    # default choice for conformance checking
    DEFAULT_CONSIDERED_CONSTRAINTS = ["equivalence", "always_after", "always_before", "never_together",
                                      "directly_follows", "activ_freq"]
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    PARAMETER_VARIANT_DELIMITER = "variant_delimiter"


NOISE_THRESHOLD = Parameters.NOISE_THRESHOLD
CONSIDERED_CONSTRAINTS = Parameters.CONSIDERED_CONSTRAINTS
DEFAULT_CONSIDERED_CONSTRAINTS = Parameters.DEFAULT_CONSIDERED_CONSTRAINTS
ACTIVITY_KEY = Parameters.ACTIVITY_KEY
PARAMETER_VARIANT_DELIMITER = Parameters.PARAMETER_VARIANT_DELIMITER
