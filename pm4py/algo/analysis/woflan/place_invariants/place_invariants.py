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
import numpy as np
import sympy

def compute_place_invariants(net):
    """
    We compute the NUllspace of the incidence matrix and obtain the place-invariants.
    :param net: Petri Net of which we want to know the place invariants.
    :return: Set of place invariants of the given Petri Net.
    """

    def compute_incidence_matrix(net):
        """
        Given a Petri Net, the incidence matrix is computed. An incidence matrix has n rows (places) and m columns
        (transitions).
        :param net: Petri Net object
        :return: Incidence matrix
        """
        n = len(net.transitions)
        m = len(net.places)
        C = np.zeros((m, n))
        i = 0
        transition_list = list(net.transitions)
        place_list = list(net.places)
        while i < n:
            t = transition_list[i]
            for in_arc in t.in_arcs:
                # arcs that go to transition
                C[place_list.index(in_arc.source), i] -= 1
            for out_arc in t.out_arcs:
                # arcs that lead away from transition
                C[place_list.index(out_arc.target), i] += 1
            i += 1
        return C

    def extract_basis_vectors(incidence_matrix):
        """
        The name of the method describes what we want t achieve. We calculate the nullspace of the transposed identity matrix.
        :param incidence_matrix: Numpy Array
        :return: a collection of numpy arrays that form a base of transposed A
        """
        # To have the same dimension as described as in https://www7.in.tum.de/~esparza/fcbook-middle.pdf and to get the correct nullspace, we have to transpose
        A = np.transpose(incidence_matrix)
        # exp from book https://www7.in.tum.de/~esparza/fcbook-middle.pdf
        x = sympy.Matrix(A).nullspace()
        # TODO: Question here: Will x be always rational? Depends on sympy implementation. Normaly, yes, we we will have rational results
        x = np.array(x).astype(np.float64)
        return x

    A = compute_incidence_matrix(net)
    return extract_basis_vectors(A)
