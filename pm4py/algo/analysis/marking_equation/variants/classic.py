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
from enum import Enum
from typing import Optional, Dict, Any, Tuple, List

import numpy as np

from pm4py.objects.petri_net.utils import align_utils, petri_utils as petri_utils
from pm4py.objects.petri_net.utils.incidence_matrix import IncidenceMatrix
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import exec_utils, constants
from pm4py.util.lp import solver


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    COSTS = "costs"
    INCIDENCE_MATRIX = "incidence_matrix"
    A = "A_matrix"
    FULL_BOOTSTRAP_REQUIRED = "full_bootstrap_required"


class MarkingEquationSolver(object):
    def __init__(self, net: PetriNet, im: Marking, fm: Marking,
                 parameters: Optional[Dict[Any, Any]] = None):
        """
        Constructor

        Parameters
        ---------------
        net
            Petri net
        im
            Initial marking
        fm
            Final marking
        parameters
            Parameters of the algorithm, including:
            - Parameters.CASE_ID_KEY => attribute to use as case identifier
            - Parameters.ACTIVITY_KEY => attribute to use as activity
            - Parameters.COSTS => (if provided) the cost function (otherwise the default cost function is applied)
            - Parameters.INCIDENCE_MATRIX => (if provided) the incidence matrix of the sync product net
            - Parameters.A => (if provided) the A numpy matrix of the incidence matrix
            - Parameters.FULL_BOOTSTRAP_REQUIRED => The preset/postset of places/transitions need to be inserted
        """
        if parameters is None:
            parameters = {}

        costs = exec_utils.get_param_value(Parameters.COSTS, parameters, None)

        if costs is None:
            costs = align_utils.construct_standard_cost_function(net, align_utils.SKIP)

        self.net = net
        self.ini = im
        self.fin = fm
        self.costs = costs
        self.incidence_matrix = exec_utils.get_param_value(Parameters.INCIDENCE_MATRIX, parameters,
                                                           IncidenceMatrix(self.net))
        self.Aeq = exec_utils.get_param_value(Parameters.A, parameters, np.asmatrix(self.incidence_matrix.a_matrix))
        self.full_bootstrap_required = exec_utils.get_param_value(Parameters.FULL_BOOTSTRAP_REQUIRED, parameters, True)

        self.__build_entities()
        self.__build_problem_components()

    def __build_entities(self):
        """
        Builds entities useful to define the marking equation
        """
        transitions = self.incidence_matrix.transitions
        self.inv_indices = {y: x for x, y in transitions.items()}
        self.inv_indices = [self.inv_indices[i] for i in range(len(self.inv_indices))]
        self.ini_vec = np.matrix(self.incidence_matrix.encode_marking(self.ini)).transpose()
        self.fin_vec = np.matrix(self.incidence_matrix.encode_marking(self.fin)).transpose()
        if self.full_bootstrap_required:
            petri_utils.decorate_transitions_prepostset(self.net)
            petri_utils.decorate_places_preset_trans(self.net)

    def __build_problem_components(self):
        """
        Builds the components needed to solve the marking equation
        """
        self.beq = self.fin_vec - self.ini_vec
        self.Aub = -np.eye(self.Aeq.shape[1])
        self.bub = np.zeros((self.Aeq.shape[1], 1))
        self.c = [self.costs[self.inv_indices[i]] for i in range(len(self.inv_indices))]
        if solver.DEFAULT_LP_SOLVER_VARIANT == solver.CVXOPT_SOLVER_CUSTOM_ALIGN:
            from cvxopt import matrix

            self.Aeq_transf = matrix(self.Aeq.astype(np.float64))
            self.Aub_transf = matrix(self.Aub.astype(np.float64))
            self.c_transf = matrix([1.0 * x for x in self.c])
        else:
            self.Aeq_transf = self.Aeq
            self.Aub_transf = self.Aub
            self.c_transf = self.c

    def get_components(self) -> Tuple[Any, Any, Any, Any, Any]:
        """
        Retrieve the components (Numpy matrixes) of the problem

        Returns
        ---------------
        c
            objective function
        Aub
           Inequalities matrix
        bub
            Inequalities vector
        Aeq
            Equalities matrix
        beq
            Equalities vector
        """
        if solver.DEFAULT_LP_SOLVER_VARIANT == solver.CVXOPT_SOLVER_CUSTOM_ALIGN:
            from cvxopt import matrix

            self.beq_transf = matrix(self.beq.astype(np.float64))
            self.bub_transf = matrix(self.bub.astype(np.float64))
        else:
            self.beq_transf = self.beq
            self.bub_transf = self.bub

        return self.c_transf, self.Aub_transf, self.bub_transf, self.Aeq_transf, self.beq_transf

    def change_ini_vec(self, ini: Marking):
        """
        Changes the initial marking of the synchronous product net

        Parameters
        --------------
        ini
            Initial marking
        """
        self.ini = ini
        self.ini_vec = np.matrix(self.incidence_matrix.encode_marking(ini)).transpose()
        self.beq = self.fin_vec - self.ini_vec

    def get_x_vector(self, sol_points: List[int]) -> List[int]:
        """
        Returns the x vector of the solution

        Parameters
        --------------
        sol_points
            Solution of the integer problem

        Returns
        ---------------
        x
            X vector
        """
        return sol_points

    def get_h(self, sol_points: List[int]) -> int:
        """
        Returns the value of the heuristics

        Parameters
        --------------
        sol_points
            Solution of the integer problem

        Returns
        --------------
        h
            Heuristics value
        """
        return int(np.dot(sol_points, self.c))

    def get_activated_transitions(self, sol_points: List[int]) -> List[PetriNet.Transition]:
        """
        Gets the transitions of the synchronous product net that are non-zero
        in the solution of the marking equation

        Parameters
        --------------
        sol_points
            Solution of the integer problem

        Returns
        --------------
        act_trans
            Activated transitions
        """
        act_trans = []
        for i in range(len(sol_points)):
            for j in range(sol_points[i]):
                act_trans.append(self.inv_indices[i])
        return act_trans

    def solve(self) -> Tuple[int, List[int]]:
        """
        Solves the marking equation, returning the heuristics and the x vector

        Returns
        -------------
        h
            Heuristics value
        x
            X vector
        """
        c, Aub, bub, Aeq, beq = self.get_components()
        return self.solve_given_components(c, Aub, bub, Aeq, beq)

    def solve_given_components(self, c, Aub, bub, Aeq, beq):
        """
        Solves the linear problem given the components

        Parameters
        --------------
        c
            Objective vector
        Aub
            Inequalities matrix
        bub
            Inequalities vector
        Aeq
            Equalities matrix
        beq
            Equalities vector

        Returns
        -------------
        h
            Heuristics value
        x
            X vector
        """
        if solver.DEFAULT_LP_SOLVER_VARIANT == solver.CVXOPT_SOLVER_CUSTOM_ALIGN and type(c) is list:
            from cvxopt import matrix
            Aub = matrix(Aub.astype(np.float64))
            bub = matrix(bub.astype(np.float64))
            Aeq = matrix(Aeq.astype(np.float64))
            beq = matrix(beq.astype(np.float64))
            c = matrix([1.0 * x for x in c])
        sol = solver.apply(c, Aub, bub, Aeq, beq, variant=solver.DEFAULT_LP_SOLVER_VARIANT)
        sol_points = solver.get_points_from_sol(sol, variant=solver.DEFAULT_LP_SOLVER_VARIANT)
        if sol_points is not None:
            x = self.get_x_vector(sol_points)
            x = [int(y) for y in x]
            h = self.get_h(sol_points)
            return h, x
        return None, None

    def get_firing_sequence(self, x: List[int]) -> Tuple[List[PetriNet.Transition], bool, int]:
        """
        Gets a firing sequence from the X vector

        Parameters
        ----------------
        x
            X vector

        Returns
        ----------------
        firing_sequence
            Firing sequence
        reach_fm
            Boolean value that is true whether the firing sequence reaches the final marking
        explained_events
            Number of explaned events by the firing sequence
        """
        activated_transitions = self.get_activated_transitions(x)
        firing_sequence, reach_fm, explained_events = align_utils.search_path_among_sol(self.net, self.ini,
                                                                                        self.fin,
                                                                                        activated_transitions)
        return firing_sequence, reach_fm, explained_events


def build(net: PetriNet, im: Marking, fm: Marking,
          parameters: Optional[Dict[Any, Any]] = None) -> MarkingEquationSolver:
    """
    Builds the marking equation out of a Petri net

    Parameters
    ---------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY => attribute to use as case identifier
        - Parameters.ACTIVITY_KEY => attribute to use as activity
        - Parameters.COSTS => (if provided) the cost function (otherwise the default cost function is applied)
        - Parameters.INCIDENCE_MATRIX => (if provided) the incidence matrix of the Petri net
        - Parameters.A => (if provided) the A numpy matrix of the incidence matrix
        - Parameters.FULL_BOOTSTRAP_REQUIRED => The preset/postset of places/transitions need to be inserted
    """
    if parameters is None:
        parameters = {}

    return MarkingEquationSolver(net, im, fm, parameters=parameters)


def get_h_value(solver: MarkingEquationSolver, parameters: Optional[Dict[Any, Any]] = None) -> int:
    """
    Gets the heuristics value from the marking equation

    Parameters
    --------------
    solver
        Marking equation solver (class in this file)
    parameters
        Possible parameters of the algorithm
    """
    return solver.solve()[0]
