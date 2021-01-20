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
from pm4py.simulation.tree_playout.variants import basic_playout, extensive, topbottom
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    BASIC_PLAYOUT = basic_playout
    EXTENSIVE = extensive
    TOPBOTTOM = topbottom


DEFAULT_VARIANT = Variants.TOPBOTTOM


def apply(tree, variant=DEFAULT_VARIANT, parameters=None):
    """
    Performs a playout of a process tree

    Parameters
    ---------------
    tree
        Process tree
    variant
        Variant of the algorithm:
        - Variants.BASIC_PLAYOUT: basic playout
        - Variants.EXTENSIVE: extensive playout (all the possible traces)
    parameters
        Parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(tree, parameters=parameters)
