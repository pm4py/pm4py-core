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


def unroll(value):
    if isinstance(value, Enum):
        return value.value
    return value


# this function can be moved to a util when string values of the parameters are no longer supported. (or is no longer needed ;-))
def get_param_value(p, parameters, default):
    if parameters is None:
        return unroll(default)
    unrolled_parameters = {}
    for p0 in parameters:
        unrolled_parameters[unroll(p0)] = parameters[p0]
    if p in parameters:
        val = parameters[p]
        return unroll(val)
    up = unroll(p)
    if up in unrolled_parameters:
        val = unrolled_parameters[up]
        return unroll(val)
    return unroll(default)


def get_variant(variant):
    if isinstance(variant, Enum):
        return variant.value
    return variant
