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

from pm4py.algo.transformation.ocel.description.variants import variant1
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    VARIANT1 = variant1


def apply(ocel: OCEL, variant=Variants.VARIANT1, parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Gets a textual representation from an object-centric event log

    Parameters
    --------------
    ocel
        Object-centric event log
    variant
        Variant of the algorithm to be used, possible values:
        - Variants.VARIANT1
    parameters
        Variant-specific parameters

    Returns
    --------------
    ocel_stri
        A textual representation of the object-centric event log
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(ocel, parameters=parameters)
