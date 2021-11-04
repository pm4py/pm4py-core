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

from pm4py.objects.dfg.exporter.variants import classic
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC


def apply(dfg, output_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Exports a DFG

    Parameters
    ---------------
    dfg
        Directly-Follows Graph
    output_path
        Output path
    variant
        Variants of the exporter, possible values:
            - Variants.CLASSIC: exporting to a .dfg file
    parameters
        Variant-specific parameters
    """
    exec_utils.get_variant(variant).apply(dfg, output_path, parameters=parameters)


def serialize(dfg, variant=DEFAULT_VARIANT, parameters=None):
    """
    Serializes a DFG object into a binary string

    Parameters
    --------------
    dfg
        DFG
    variant
        Variants of the exporter, possible values:
            - Variants.CLASSIC: exporting to a .dfg file
    parameters
        Variant-specific parameters

    Returns
    --------------
    serialization
        String that represents the DFG
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).export_as_string(dfg, parameters=parameters)
