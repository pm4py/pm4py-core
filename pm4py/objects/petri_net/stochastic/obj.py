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
