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

from pm4py.algo.analysis.workflow_net.variants import petri_net
from pm4py.util import exec_utils
from typing import Optional, Dict, Any
from pm4py.objects.petri_net.obj import PetriNet


class Variants(Enum):
    PETRI_NET = petri_net


def apply(net: PetriNet, parameters: Optional[Dict[Any, Any]] = None, variant=Variants.PETRI_NET) -> bool:
    """
    Checks if a Petri net is a workflow net

    Parameters
    ---------------
    net
        Petri net
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm, possibe values:
        - Variants.PETRI_NET

    Returns
    ---------------
    boolean
        Boolean value
    """
    return exec_utils.get_variant(variant).apply(net, parameters=parameters)
