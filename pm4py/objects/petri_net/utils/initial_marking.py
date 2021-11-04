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
from pm4py.objects.petri_net.obj import Marking


def discover_initial_marking(petri):
    """
    Discovers initial marking from a Petri net

    Parameters
    ------------
    petri
        Petri net

    Returns
    ------------
    initial_marking
        Initial marking of the Petri net
    """
    initial_marking = Marking()

    for place in petri.places:
        if len(place.in_arcs) == 0:
            initial_marking[place] = 1

    return initial_marking
