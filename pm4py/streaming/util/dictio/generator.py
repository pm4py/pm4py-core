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

from pm4py.streaming.util.dictio.versions import classic, thread_safe, redis
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic
    THREAD_SAFE = thread_safe
    REDIS = redis


DEFAULT_VARIANT = Variants.THREAD_SAFE


def apply(variant=DEFAULT_VARIANT, parameters=None):
    """
    Generates a Python dictionary object
    (different implementations are possible)

    Parameters
    ----------------
    variant
        Variant to use
    parameters
        Parameters to use in the generation

    Returns
    -----------------
    dictio
        Dictionary
    """
    return exec_utils.get_variant(variant).apply(parameters=parameters)
