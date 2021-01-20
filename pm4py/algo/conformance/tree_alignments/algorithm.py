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
from pm4py.algo.conformance.tree_alignments.variants.approximated import matrix_lp as approximated_matrix_lp
from pm4py.algo.conformance.tree_alignments.variants.approximated import original as approximated_original

from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    APPROXIMATED_ORIGINAL = approximated_original
    APPROXIMATED_MATRIX_LP = approximated_matrix_lp


DEFAULT_VARIANT = Variants.APPROXIMATED_MATRIX_LP


def apply(obj, pt, variant=DEFAULT_VARIANT, parameters=None):
    """
    Align an event log or a trace with a process tree

    Parameters
    --------------
    obj
        Log / Trace
    pt
        Process tree
    variant
        Variant
    parameters
        Variant-specific parameters

    Returns
    --------------
    alignments
        Alignments
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(obj, pt, parameters=parameters)
