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
from copy import copy
from pm4py.util.lp import solver
from pm4py.util import constants
import warnings
import importlib.util


def removearray(L, arr):
    """
    Remove an array from a given list and return the list with the removed element.
    :param L: list object
    :param arr: array that has to be removed
    :return: list object without array
    """
    ind = 0
    size = len(L)
    while ind != size and not np.array_equal(L[ind], arr):
        ind += 1
    if ind != size:
        L.pop(ind)
    else:
        raise ValueError('array not found in list.')

def transform_basis(basis, style=None):
    """
    We construct a (I)LP to transform our basis into a set of vectors by using linear combination to fit certain styles/
    properties
    :param basis: list of p-invariants. Commonly computed by the method 'compute_place_invariants' in
    place_invariants.py
    :param style: String that is used to construct certain constraints
    At the moment, 'uniform' (all weights have value 0 or 1), and 'weighted' (all weights are >=0) are supported
    :return: List of p-invariants that fits the style
    """
    if style==None:
        style='weighted'

    # First, we want to check if a vector of a basis only contains non-positve entries. If so, then we multiply the
    # vector -1.
    modified_base = []
    for vector in basis:
        all_non_positiv = True
        for entry in vector:
            if entry > 0:
                all_non_positiv = False
        if all_non_positiv:
            modified_base.append(-1 * vector)
        else:
            modified_base.append(vector)
    #For uniform variants, it is necessary that the weight for a place is either 0 or 1. We collect the variants for
    #which this condition does not hold. We also collect the variants for the weighted invariants the entry is <0.
    to_modify = []

    for vector in modified_base:
        for entry in vector:
            if ((entry < 0 or entry > 1) and style=='uniform') or ( entry < 0 and style=='weighted'):
                to_modify.append(vector)
                break
    # if we have nothing to modify, we are done
    if len(to_modify) > 0:
        for vector in to_modify:
            removearray(modified_base, vector)
            set_B = range(0, len(modified_base))
            # start of the problem
            """prob = pulp.LpProblem("linear_combination", pulp.LpMinimize)
            X = pulp.LpVariable.dicts("x", set_B, cat='Integer')
            y = pulp.LpVariable("y", cat='Integer', lowBound=1)
            # add objective
            prob += pulp.lpSum(X[i] for i in set_B)
            if style=='uniform':
                # variables for uniform. Therefore, the resulting weight can either be 0 or 1
                z = pulp.LpVariable.dicts("z", range(0, len(vector)), lowBound=0, upBound=1, cat='Integer')
                # add constraints
                for i in range(len(vector)):
                    prob += pulp.lpSum(X[j]*modified_base[j][i] for j in range(len(modified_base)))+y*vector[i]== z[i]
            elif style=='weighted':
                for i in range(len(vector)):
                    prob += pulp.lpSum(X[j]*modified_base[j][i] for j in range(len(modified_base)))+y*vector[i] >= 0
            prob.solve()"""
            # problem is solved

            c = [1]*len(set_B) + [0] * (len(vector) + 1)
            zeros = [0] * (len(set_B) + len(vector) + 1)
            Aub = []
            bub = []
            Aeq = []
            beq = []
            first_constraint = copy(zeros)
            first_constraint[len(set_B)] = -1
            Aub.append(first_constraint)
            bub.append(-1)
            for i in range(len(vector)):
                this_row = copy(zeros)
                this_row[len(set_B)] = list(vector[i])[0]
                for j in range(len(modified_base)):
                    this_row[j] = list(modified_base[j][i])[0]

                if style == "uniform":
                    this_row[len(set_B) + 1 + i] = -1

                if style == "uniform":
                    Aeq.append(this_row)
                    beq.append(0)
                elif style == "weighted":
                    Aub.append([-x for x in this_row])
                    bub.append(0)
            for i in range(len(vector)):
                last_constraint_1 = copy(zeros)
                last_constraint_1[len(set_B) + 1 + i] = 1
                Aub.append(last_constraint_1)
                bub.append(1)
                last_constraint_2 = copy(zeros)
                last_constraint_2[len(set_B) + 1 + i] = -1
                Aub.append(last_constraint_2)
                bub.append(0)

            Aeq = np.asmatrix(Aeq).astype(np.float64)
            beq = np.asmatrix(beq).transpose().astype(np.float64)
            Aub = np.asmatrix(Aub).astype(np.float64)
            bub = np.asmatrix(bub).transpose().astype(np.float64)

            if Aeq.shape[1] == 0:
                Aeq = np.zeros((1, len(c))).astype(np.float64)
                beq = np.zeros(1).transpose().astype(np.float64)

            if Aub.shape[1] == 0:
                Aub = np.zeros((1, len(c))).astype(np.float64)
                bub = np.zeros(1).transpose().astype(np.float64)

            # this is highly critical and LP solutions are not always correct :(

            proposed_solver = solver.SCIPY
            if importlib.util.find_spec("pulp"):
                proposed_solver = solver.PULP
            else:
                if constants.SHOW_INTERNAL_WARNINGS:
                    warnings.warn("solution from scipy may be unstable. Please install PuLP (pip install pulp) for fully reliable results.")

            sol = solver.apply(c, Aub, bub, Aeq, beq, variant=proposed_solver, parameters={"method": "revised simplex", "require_ilp": True})
            points = solver.get_points_from_sol(sol, variant=proposed_solver)
            val = solver.get_prim_obj_from_sol(sol, variant=proposed_solver)

            if points is not None:
                new_vector = np.zeros(len(vector))

                if style == "weighted":
                    for i in range(len(new_vector)):
                        new_vector[i] = points[len(set_B)] * vector[i]
                        for j in range(len(modified_base)):
                            new_vector[i] = new_vector[i] + modified_base[j][i] * points[j]
                elif style == "uniform":
                    for i in range(len(new_vector)):
                        new_vector[i] = points[len(set_B) + 1 + i]

                new_vector = np.array([new_vector]).T
                modified_base.append(new_vector)

    return modified_base


def compute_uncovered_places(invariants, net):
    """
    Compute a list of uncovered places for invariants of a given Petri Net. Note that there exists a separate algorithm
    for s-components
    :param invariants: list of invariants. Each invariants is a numpy-Array representation
    :param net: Petri Net object of PM4Py
    :return: List of uncovered place over all invariants
    """
    place_list=sorted(list(net.places), key=lambda x: x.name)
    unncovered_list=place_list.copy()
    for invariant in invariants:
        for index, value in enumerate(invariant):
            if value != 0:
                if place_list[index] in unncovered_list:
                    unncovered_list.remove(place_list[index])
    return unncovered_list
