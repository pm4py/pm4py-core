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
from pm4py.streaming.algo.conformance.tbr.variants import classic


class Variants(Enum):
    CLASSIC = classic


def apply(net, im, fm, variant=Variants.CLASSIC, parameters=None):
    """
    Method that creates the TbrStreamingConformance object

    Parameters
    ----------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    variant
        Variant of the algorithm to use, possible:
            - Variants.CLASSIC
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    conf_stream_obj
        Conformance streaming object
    """
    return exec_utils.get_variant(variant).apply(net, im, fm, parameters=parameters)
