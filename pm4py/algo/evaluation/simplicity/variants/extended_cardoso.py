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

from pm4py.objects.petri_net.obj import PetriNet
from typing import Optional, Dict, Any


def apply(petri_net: PetriNet, parameters: Optional[Dict[Any, Any]] = None) -> float:
    """
    Computes the extended Cardoso metric as described in the paper:

    "Complexity Metrics for Workflow Nets"
    Lassen, Kristian Bisgaard, and Wil MP van der Aalst

    Parameters
    -------------
    petri_net
        Petri net

    Returns
    -------------
    ext_cardoso_metric
        Extended Cardoso metric
    """
    if parameters is None:
        parameters = {}

    ext_card = 0

    for place in petri_net.places:
        targets = set()
        for out_arc in place.out_arcs:
            for out_arc2 in out_arc.target.out_arcs:
                targets.add(out_arc2.target)
        ext_card += len(targets)

    return ext_card
