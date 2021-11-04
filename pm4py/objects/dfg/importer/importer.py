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

from pm4py.objects.dfg.importer.variants import classic
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC


def apply(file_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Import a DFG (along with the start and end activities)

    Parameters
    --------------
    file_path
        Path of the DFG file
    variant
        Variant of the importer, possible values:
            - Variants.CLASSIC: importing from a .dfg file
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    return exec_utils.get_variant(variant).apply(file_path, parameters=parameters)


def deserialize(dfg_string, variant=DEFAULT_VARIANT, parameters=None):
    """
    Import a DFG from a binary/textual string

    Parameters
    --------------
    dfg_string
        DFG represented as a string in the .dfg format
    variant
        Variant of the importer, possible values:
            - Variants.CLASSIC: importing from a .dfg file
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    return exec_utils.get_variant(variant).import_dfg_from_string(dfg_string, parameters=parameters)
