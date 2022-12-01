from typing import Dict, List, Tuple
from pm4py.objects.petri_net.stochastic.obj import StochasticPetriNet


class StochasticArcWeightNet(StochasticPetriNet):
    '''
    Petri nets with stochastic arc weights. Arcs are assumed to desribe distributions of token consumption/production.
    We utilize the weight attribute that is defined in the Petri net based class to store the distribution.
    '''

    class Arc(StochasticPetriNet.Arc):

        def __init__(self, source, target, weight={1: 1.0}, properties=None):
            super().__init__(source, target, weight, properties)

        def __get_weight_distribution(self) -> Dict[int, float]:
            return self.weight

        weight_distribution = property(__get_weight_distribution)


    Binding = List[Tuple[Arc, int]]
