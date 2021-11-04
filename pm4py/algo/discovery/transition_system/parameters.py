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
from pm4py.util import constants

import warnings
warnings.warn("pm4py.algo.discovery.transition_system.parameters is deprecated. Please use the variant-specific parameters.")


class Parameters(Enum):
    VIEW_MULTI_SET = 'multiset'
    VIEW_SET = 'set'
    VIEW_SEQUENCE = 'sequence'

    VIEWS = {VIEW_MULTI_SET, VIEW_SET, VIEW_SEQUENCE}

    DIRECTION_FORWARD = 'forward'
    DIRECTION_BACKWARD = 'backward'
    DIRECTIONS = {DIRECTION_FORWARD, DIRECTION_BACKWARD}

    PARAM_KEY_VIEW = 'view'
    PARAM_KEY_WINDOW = 'window'
    PARAM_KEY_DIRECTION = 'direction'

    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY

    INCLUDE_DATA = 'include_data'
