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
from pm4py.objects.process_tree.exporter.variants import ptml
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    PTML = ptml


DEFAULT_VARIANT = Variants.PTML


def apply(tree, output_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Exports the process tree to a file

    Parameters
    ----------------
    tree
        Process tree
    output_path
        Output path
    variant
        Variant of the algorithm:
            - Variants.PTML
    parameters
        Parameters
    """
    return exec_utils.get_variant(variant).apply(tree, output_path, parameters=parameters)


def serialize(tree, variant=DEFAULT_VARIANT, parameters=None):
    """
    Serializes the process tree into a binary string

    Parameters
    ----------------
    tree
        Process tree
    variant
        Variant of the algorithm:
            - Variants.PTML
    parameters
        Parameters

    Returns
    ---------------
    serialization
        Serialized string
    """
    return exec_utils.get_variant(variant).export_tree_as_string(tree, parameters=parameters)
