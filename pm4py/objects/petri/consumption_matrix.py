"""
Implements the consumption matrix as explained in the following paper:

van Dongen, Boudewijn F. "Efficiently computing alignments." International Conference on Business Process Management.
Springer, Cham, 2018.
https://link.springer.com/chapter/10.1007/978-3-319-98648-7_12
"""

from typing import Dict

import numpy as np

from pm4py.objects.petri.obj import PetriNet


class ConsumptionMatrix(object):
    def __init__(self, net: PetriNet):
        """
        Constructor

        Parameters
        --------------
        net
            Petri net
        """
        self.__place_indices = {}
        self.__transition_indices = {}
        self.__C = None
        places = sorted([x for x in net.places], key=lambda x: (x.name, id(x)))
        transitions = sorted([x for x in net.transitions], key=lambda x: (x.name, id(x)))

        for p in places:
            self.__place_indices[p] = len(self.__place_indices)
        for t in transitions:
            self.__transition_indices[t] = len(self.__transition_indices)
        self.__compute_C_matrix(net)

    def __compute_C_matrix(self, net: PetriNet):
        """
        Builds the C matrix

        Parameters
        ---------------
        net
            Petri net
        """
        inv_indices = {y: x for x, y in self.__transition_indices.items()}
        inv_indices = [inv_indices[i] for i in range(len(inv_indices))]
        self.__C = [[0 for i in range(len(self.__transition_indices))] for j in range(len(self.__place_indices))]
        for p in net.places:
            outgoing_trans = [a.target for a in p.out_arcs]
            self.__C[self.__place_indices[p]] = [-1 if inv_indices[i] in outgoing_trans else 0 for i in
                                                 range(len(inv_indices))]

    def __get_transition_indices(self) -> Dict[PetriNet.Transition, int]:
        """
        Gets the transitions in the order in which they have been inserted in the consumption matrix

        Returns
        -------------
        trans_indices
            Dictionary associating to each transition an incremental number
        """
        return self.__transition_indices

    def __get_place_indices(self) -> Dict[PetriNet.Place, int]:
        """
        Gets the places in the order in which they have been inserted in the consumption matrix

        Returns
        -------------
        place_indices
            Dictionary associating to each place an incremental number
        """
        return self.__place_indices

    def __get_c_matrix(self) -> np.ndarray:
        """
        Gets the Numpy representation of the consumption matrix

        Returns
        -------------
        C
            C matrix
        """
        return self.__C

    places = property(__get_place_indices)
    transitions = property(__get_transition_indices)
    c_matrix = property(__get_c_matrix)


def construct(net: PetriNet) -> ConsumptionMatrix:
    """
    Construct a consumption matrix given a Petri net

    Parameters
    ----------------
    net
        Petri net

    Returns
    ---------------
    cons_mat
        Consumption matrix object
    """
    return ConsumptionMatrix(net)
