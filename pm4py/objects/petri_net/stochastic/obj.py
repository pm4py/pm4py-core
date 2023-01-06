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

from typing import Any, Collection, Dict

from pm4py.objects.petri_net.obj import PetriNet


class StochasticPetriNet(PetriNet):

    class Transition(PetriNet.Transition):
        def __init__(self, name: str, label: str = None, in_arcs: Collection[PetriNet.Arc] = None, out_arcs: Collection[PetriNet.Arc] = None, weight: float = 1.0, properties: Dict[str, Any] = None):
            super().__init__(name, label, in_arcs, out_arcs, properties)
            self.__weight = weight

        def __set_weight(self, weight: float):
            self.__weight = weight

        def __get_weight(self) -> float:
            return self.__weight

        weight = property(__get_weight, __set_weight)
