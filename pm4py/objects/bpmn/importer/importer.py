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

from pm4py.objects.bpmn.importer.variants import lxml
from pm4py.util import exec_utils


class Variants(Enum):
    LXML = lxml


DEFAULT_VARIANT = Variants.LXML


def apply(path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Imports a BPMN diagram from a file

    Parameters
    -------------
    path
        Path to the file
    variant
        Variant of the algorithm to use, possible values:
        - Variants.LXML
    parameters
        Parameters of the algorithm

    Returns
    -------------
    bpmn_graph
        BPMN graph
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(path, parameters=parameters)


def deserialize(bpmn_string, variant=DEFAULT_VARIANT, parameters=None):
    """
    Deserialize a text/binary string representing a BPMN 2.0

    Parameters
    -------------
    bpmn_string
        BPMN string
    variant
        Variant of the algorithm to use, possible values:
        - Variants.LXML
    parameters
        Parameters of the algorithm

    Returns
    -------------
    bpmn_graph
        BPMN graph
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).import_from_string(bpmn_string, parameters=parameters)
