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
from pm4py.util import exec_utils
from pm4py.streaming.algo.conformance.footprints.variants import classic


class Variants(Enum):
    CLASSIC = classic


def apply(footprints, variant=Variants.CLASSIC, parameters=None):
    """
    Gets a footprints conformance checking object

    Parameters
    --------------
    footprints
        Footprints object (calculated from an entire log, from a process tree ...)
    variant
        Variant of the algorithm. Possible values: Variants.CLASSIC
    parameters
        Parameters of the algorithm

    Returns
    --------------
    fp_check_obj
        Footprints conformance checking object
    """
    return exec_utils.get_variant(variant).apply(footprints, parameters=parameters)
