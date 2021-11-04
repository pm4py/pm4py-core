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

from pm4py.objects.bpmn.exporter.variants import etree
from pm4py.util import exec_utils


class Variants(Enum):
    ETREE = etree


DEFAULT_VARIANT = Variants.ETREE


def apply(bpmn_graph, target_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Exports the BPMN diagram to a file

    Parameters
    -------------
    bpmn_graph
        BPMN diagram
    target_path
        Target path
    variant
        Variant of the algorithm to use, possible values:
        - Variants.ETREE
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(bpmn_graph, target_path, parameters=parameters)


def serialize(bpmn_graph, variant=DEFAULT_VARIANT, parameters=None):
    """
    Serializes the BPMN object into a binary string

    Parameters
    -------------
    bpmn_graph
        BPMN diagram
    variant
        Variant of the algorithm to use, possible values:
        - Variants.ETREE
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    serialization
        Binary string (BPMN 2.0 XML standard)
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).get_xml_string(bpmn_graph, parameters=parameters)
