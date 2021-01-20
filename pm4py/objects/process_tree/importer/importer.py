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

from pm4py.objects.process_tree.importer.variants import ptml
from pm4py.util import exec_utils


class Variants(Enum):
    PTML = ptml


DEFAULT_VARIANT = Variants.PTML


def apply(file_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Imports a process tree from the specified path

    Parameters
    ---------------
    path
        Path
    variant
        Variant of the algorithm, possible values:
            - Variants.PTML
    parameters
        Possible parameters (version specific)

    Returns
    ---------------
    tree
        Process tree
    """
    return exec_utils.get_variant(variant).apply(file_path, parameters=parameters)


def deserialize(tree_string, variant=DEFAULT_VARIANT, parameters=None):
    """
    Deserialize a text/binary string representing a process tree in the PTML format

    Parameters
    ----------
    tree_string
        Process tree expressed as PTML string
    variant
        Variant of the algorithm, possible values:
            - Variants.PTML
    parameters
        Other parameters of the algorithm

    Returns
    ----------
    tree
        Process tree
    """
    return exec_utils.get_variant(variant).import_tree_from_string(tree_string, parameters=parameters)
