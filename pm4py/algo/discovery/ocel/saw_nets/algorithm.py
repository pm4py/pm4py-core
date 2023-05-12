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
from pm4py.util import exec_utils
from pm4py.algo.discovery.ocel.saw_nets.variants import classic
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


class Variants(Enum):
    CLASSIC = classic


def apply(ocel: OCEL, variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discovers a SAW net representing the behavior of the provided object-centric event log.

    Parameters
    ----------------
    ocel
        Object-centric event log
    variant
        The variant of the algorithm to be used, possible values: Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    ---------------
    Dictionary with the following keys:
        - ot_saw_net => the SAW nets for the single object types
        - multi_saw_net => the overall SAW net
        - decorations_multi_saw_net => decorations for the visualization of the SAW net
    """
    return exec_utils.get_variant(variant).apply(ocel, parameters)
