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
from typing import Dict

from pm4py.objects.petri.petrinet import PetriNet


def check_soundness(petri_net: PetriNet, initial_marking: Dict[PetriNet.Place, int],
                    final_marking: Dict[PetriNet.Place, int]) -> bool:
    """
    Check if a given Petri net is a sound WF-net.
    A Petri net is a WF-net iff:
        - it has a unique source place
        - it has a unique end place
        - every element in the WF-net is on a path from the source to the sink place
    A WF-net is sound iff:
        - it contains no live-locks
        - it contains no deadlocks
        - we are able to always reach the final marking
    For a formal definition of sound WF-net, consider: http://www.padsweb.rwth-aachen.de/wvdaalst/publications/p628.pdf


    Parameters
    ---------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    --------------
    boolean
        Soundness
    """
    from pm4py.evaluation.soundness.woflan import algorithm as woflan
    return woflan.apply(petri_net, initial_marking, final_marking)
