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
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.algo.discovery.ocel.ocdfg.variants import classic
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


def apply(ocel: OCEL, variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discovers an OC-DFG model from an object-centric event log
    Reference paper:
    Berti, Alessandro, and Wil van der Aalst. "Extracting multiple viewpoint models from relational databases." Data-Driven Process Discovery and Analysis. Springer, Cham, 2018. 24-51.

    Parameters
    ----------------
    ocel
        Object-centric event log
    variant
        Variant of the algorithm to use:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    ----------------
    ocdfg
        Object-centric directly-follows graph
    """
    return exec_utils.get_variant(variant).apply(ocel, parameters)
