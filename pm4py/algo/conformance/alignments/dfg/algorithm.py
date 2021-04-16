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
from pm4py.algo.conformance.alignments.dfg.variants import classic
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


def apply(obj, dfg, sa, ea, variant=Variants.CLASSIC, parameters=None):
    """
    Applies the alignment algorithm provided a log/trace object, and a *connected* DFG

    Parameters
    --------------
    obj
        Event log / Trace
    dfg
        *Connected* directly-Follows Graph
    sa
        Start activities
    ea
        End activities
    variant
        Variant of the DFG alignments to be used. Possible values:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters.

    Returns
    --------------
    ali
        Result of the alignment
    """
    return exec_utils.get_variant(variant).apply(obj, dfg, sa, ea, parameters=parameters)
