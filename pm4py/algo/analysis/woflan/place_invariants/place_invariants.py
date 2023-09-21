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
        transition_list = sorted(list(net.transitions), key=lambda x: x.name)
        place_list = sorted(list(net.places), key=lambda x: x.name)
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

    def rref(A, tol=1.0e-12):
        m, n = A.shape
        i, j = 0, 0
        jb = []

        while i < m and j < n:
            # Find value and index of largest element in the remainder of column j
            k = np.argmax(np.abs(A[i:m, j])) + i
            p = np.abs(A[k, j])
            if p <= tol:
                # The column is negligible, zero it out
                A[i:m, j] = 0.0
                j += 1
            else:
                # Remember the column index
                jb.append(j)
                if i != k:
                    # Swap the i-th and k-th rows
                    A[[i, k], j:n] = A[[k, i], j:n]
                # Divide the pivot row i by the pivot element A[i, j]
                A[i, j:n] = A[i, j:n] / A[i, j]
                # Subtract multiples of the pivot row from all the other rows
                for k in range(m):
                    if k != i:
                        A[k, j:n] -= A[k, j] * A[i, j:n]
                i += 1
                j += 1
        # Finished
        return A, jb

    def extract_basis_vectors(incidence_matrix):
        """
        The name of the method describes what we want t achieve. We calculate the nullspace of the transposed identity matrix.
        :param incidence_matrix: Numpy Array
        :return: a collection of numpy arrays that form a base of transposed A
        """
        # To have the same dimension as described as in https://www7.in.tum.de/~esparza/fcbook-middle.pdf and to get the correct nullspace, we have to transpose
        A = np.transpose(incidence_matrix)
        reduced, pivots = rref(A)
        free_vars = [i for i in range(A.shape[1]) if i not in pivots]
        basis = []

        for free_var in free_vars:
            vec = np.zeros(A.shape[1])
            vec[free_var] = 1
            for piv_row, piv_col in enumerate(pivots):
                vec[piv_col] -= reduced[piv_row, free_var]
            basis.append(vec.tolist())

        z = [[] for k in range(len(basis))]
        if basis:
            for i in range(len(basis[0])):
                for k in range(len(basis)):
                    z[k].append([basis[k][i]])
        z = np.array(z)

        return z

    A = compute_incidence_matrix(net)
    return extract_basis_vectors(A)
