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
from typing import Optional, Dict, Any

from pm4py.objects.ocel.importer.xmlocel.variants import classic, ocel20, ocel20_rustxes
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic
    OCEL20 = ocel20
    OCEL20_RUSTXES = ocel20_rustxes


def apply(file_path: str, variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Imports an object-centric event log from a XML-OCEL file

    Parameters
    -----------------
    file_path
        Path to the XML-OCEL file
    variant
        Variant of the algorithm to use, possible values:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    ------------------
    ocel
        Object-centric event log
    """
    return exec_utils.get_variant(variant).apply(file_path, parameters)
