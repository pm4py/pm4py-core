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
from typing import Optional, Dict
from typing import Tuple, List, Any

import numpy as np

from pm4py.objects.log.obj import Trace
from pm4py.objects.petri_net.utils import align_utils, petri_utils as petri_utils
from pm4py.objects.petri_net.utils.consumption_matrix import ConsumptionMatrix
from pm4py.objects.petri_net.utils.incidence_matrix import IncidenceMatrix
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import exec_utils, constants, xes_constants, points_subset
from pm4py.util.lp import solver


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    MAX_K_VALUE = "max_k_value"
    COSTS = "costs"
    SPLIT_IDX = "split_idx"
    INCIDENCE_MATRIX = "incidence_matrix"
    A = "A_matrix"
    CONSUMPTION_MATRIX = "consumption_matrix"
    C = "C_matrix"
    FULL_BOOTSTRAP_REQUIRED = "full_bootstrap_required"


"""
Implements the extended marking equation as explained in the following paper:

van Dongen, Boudewijn F. "Efficiently computing alignments." International Conference on Business Process Management.
Springer, Cham, 2018.
https://link.springer.com/chapter/10.1007/978-3-319-98648-7_12
"""


class ExtendedMarkingEquationSolver(object):
    def __init__(self, trace: Trace, sync_net: PetriNet, sync_im: Marking, sync_fm: Marking,
                 parameters: Optional[Dict[Any, Any]] = None):
        """
        Constructor

        Parameters
        ---------------
        trace
            Trace
        sync_net
            Synchronous product net
        sync_im
            Initial marking
        sync_fm
            Final marking
        parameters
            Parameters of the algorithm, including:
            - Parameters.CASE_ID_KEY => attribute to use as case identifier
            - Parameters.ACTIVITY_KEY => attribute to use as activity
            - Parameters.COSTS => (if provided) the cost function (otherwise the default cost function is applied)
            - Parameters.SPLIT_IDX => (if provided) the split points as indices of elements of the trace
                (e.g. for ["A", "B", "C", "D", "E"], specifying [1,3] as split points means splitting at "B" and "D").
                If not provided, some split points at uniform distances are found.
            - Parameters.MAX_K_VALUE => the maximum number of split points that is allowed (trim the specified indexes
                if necessary).
            - Parameters.INCIDENCE_MATRIX => (if provided) the incidence matrix associated to the sync product net
            - Parameters.A => (if provided) the A numpy matrix of the incidence matrix
            - Parameters.CONSUMPTION_MATRIX => (if provided) the consumption matrix associated to the sync product net
            - Parameters.C => (if provided) the C numpy matrix of the consumption matrix
            - Parameters.FULL_BOOTSTRAP_REQUIRED => The preset/postset of places/transitions need to be inserted
        """
        if parameters is None:
            parameters = {}

        activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
        max_k_value = exec_utils.get_param_value(Parameters.MAX_K_VALUE, parameters, 5)
        costs = exec_utils.get_param_value(Parameters.COSTS, parameters, None)
        split_idx = exec_utils.get_param_value(Parameters.SPLIT_IDX, parameters, None)
        self.full_bootstrap_required = exec_utils.get_param_value(Parameters.FULL_BOOTSTRAP_REQUIRED, parameters, True)

        self.trace = [x[activity_key] for x in trace]
        if costs is None:
            costs = align_utils.construct_standard_cost_function(sync_net, align_utils.SKIP)
        if split_idx is None:
            split_idx = [i for i in range(1, len(trace))]
        self.split_idx = split_idx
        if len(self.split_idx) > max_k_value:
            self.split_idx = points_subset.pick_chosen_points_list(max_k_value, self.split_idx)
        self.k = len(self.split_idx) if len(self.split_idx) > 1 else 2
        self.sync_net = sync_net
        self.ini = sync_im
        self.fin = sync_fm
        self.costs = costs
        self.incidence_matrix = exec_utils.get_param_value(Parameters.INCIDENCE_MATRIX, parameters,
                                                           IncidenceMatrix(self.sync_net))
        self.consumption_matrix = exec_utils.get_param_value(Parameters.CONSUMPTION_MATRIX, parameters,
                                                             ConsumptionMatrix(self.sync_net))
        self.A = exec_utils.get_param_value(Parameters.A, parameters, np.asmatrix(self.incidence_matrix.a_matrix))
        self.C = exec_utils.get_param_value(Parameters.C, parameters, np.asmatrix(self.consumption_matrix.c_matrix))

        self.__build_entities()

    def __build_entities(self):
        """
        Builds entities useful to define the marking equation
        """
        self.Aeq = None
        self.__build_encodings()
        if self.full_bootstrap_required:
            petri_utils.decorate_transitions_prepostset(self.sync_net)
            petri_utils.decorate_places_preset_trans(self.sync_net)

    def __build_encodings(self):
        """
        Encodes the aforementioned objects in Numpy matrixes
        """
        self.zeros = np.zeros((self.A.shape[0], self.A.shape[1]))
        self.ini_vec = np.matrix(self.incidence_matrix.encode_marking(self.ini)).transpose()
        self.fin_vec = np.matrix(self.incidence_matrix.encode_marking(self.fin)).transpose()
        transitions = self.incidence_matrix.transitions
        self.inv_indices = {y: x for x, y in transitions.items()}
        self.inv_indices = [self.inv_indices[i] for i in range(len(self.inv_indices))]
        self.c = self.__build_cost_vector()
        self.__build_variable_corr()
        self.__build_h_value_cost_vector()
        self.c1 = list(self.c)
        self.__build_non_null_entries_y()

    def __build_cost_vector(self) -> List[int]:
        """
        Builds the complete cost vector of the integer problem
        """
        c1 = [self.costs[self.inv_indices[i]] for i in range(len(self.inv_indices))] * self.k
        c2 = [self.costs[self.inv_indices[i]] for i in range(len(self.inv_indices))] * (self.k - 1)
        c3 = [0 for i in range(len(self.inv_indices))] * (self.k - 1)
        c = c1 + c2 + c3
        return c

    def __build_h_value_cost_vector(self):
        """
        Builds the cost vector for the heuristics calculation as explained in the paper
        """
        self.c0 = list(self.c)
        for idx in self.y[-1]:
            self.c0[idx] = 0

    def __build_variable_corr(self):
        """
        The variables of the LP are split between both "x", "y" and "xy" (which is the sum of x and y)

        Make sure we can reconstruct that!
        """
        count = 0
        self.x = []
        for i in range(self.k):
            self.x.append([])
            for j in range(len(self.inv_indices)):
                self.x[-1].append(count)
                count = count + 1
        self.y = []
        for i in range(self.k - 1):
            self.y.append([])
            for j in range(len(self.inv_indices)):
                self.y[-1].append(count)
                count = count + 1
        self.xy = []
        for i in range(self.k - 1):
            self.xy.append([])
            for j in range(len(self.inv_indices)):
                self.xy[-1].append(count)
                count = count + 1

    def __build_Aeq1(self) -> np.ndarray:
        """
        Builds point (1) of the extended marking equation paper
        """
        Aeq1 = np.hstack([self.A] + (2 * self.k - 2) * [self.zeros] + (self.k - 1) * [self.A])
        return Aeq1

    def __build_Aeq2(self) -> np.ndarray:
        """
        We have some variables xy, that are the sum of x and y.
        Just make sure that xy = x + y
        (not implementing any specific point!)
        """
        Aeq_stack = []
        for i in range(1, len(self.x)):
            Aeq = np.zeros((len(self.x[i]), self.xy[-1][-1] + 1))
            for j in range(len(self.x[i])):
                Aeq[j][self.x[i][j]] = 1
                Aeq[j][self.y[i - 1][j]] = 1
                Aeq[j][self.xy[i - 1][j]] = -1
            Aeq_stack.append(Aeq)
        Aeq = np.vstack(Aeq_stack)
        return Aeq

    def __build_non_null_entries_y(self):
        """
        Utility function that is needed for point (6) of the extended marking equation paper
        """
        self.null_entries = []
        for i in self.split_idx:
            self.null_entries.append([])
            act = self.trace[i]
            for j in range(len(self.inv_indices)):
                if self.inv_indices[j].label[0] == act:
                    self.null_entries[-1].append(j)

    def __build_Aeq3(self) -> np.ndarray:
        """
        Implements point (6) of the extended marking equation paper
        """
        Aeq_stack = []
        for i in range(len(self.y)):
            Aeq = np.zeros((1, self.xy[-1][-1] + 1))
            for j in range(len(self.y[i])):
                Aeq[0][self.y[i][j]] = 1
            Aeq_stack.append(Aeq)
        Aeq = np.vstack(Aeq_stack)
        return Aeq

    def __build_Aeq4(self) -> np.ndarray:
        """
        Implements point (5) of the extended marking equation paper
        """
        Aeq = np.zeros((len(self.null_entries), self.xy[-1][-1] + 1))
        for i in range(min(len(self.null_entries), len(self.y))):
            for j in range(len(self.y[i])):
                if j not in self.null_entries[i]:
                    Aeq[i][self.y[i][j]] = 1
        return Aeq

    def __build_Aub1(self) -> np.ndarray:
        """
        Implements points (3) and (4) of the extended marking equation paper
        """
        Aub_stack = []
        for i in range(len(self.x)):
            Aub = np.zeros((len(self.x[i]), self.xy[-1][-1] + 1))
            for j in range(len(self.x[i])):
                Aub[j][self.x[i][j]] = -1
            Aub_stack.append(Aub)
        for i in range(len(self.y)):
            Aub = np.zeros((len(self.y[i]), self.xy[-1][-1] + 1))
            for j in range(len(self.y[i])):
                Aub[j][self.y[i][j]] = -1
            Aub_stack.append(Aub)
        Aub = np.vstack(Aub_stack)
        return Aub

    def __build_Aub2(self) -> np.ndarray:
        """
        Implements point (2) of the extended marking equation paper
        """
        Aub_stack = []
        for i in range(self.k - 1):
            v = [self.A]
            v = v + (self.k - 1) * [self.zeros]
            for j in range(self.k - 1):
                if j == i:
                    v = v + [self.C]
                else:
                    v = v + [self.zeros]
            for j in range(self.k - 1):
                if j < i:
                    v = v + [self.A]
                else:
                    v = v + [self.zeros]
            Aub = np.hstack(v)
            Aub_stack.append(Aub)
        Aub = np.vstack(Aub_stack)
        Aub = -Aub
        return Aub

    def __build_lin_prog_components(self):
        """
        Builds the components needed to solve the marking equation
        """
        Aeq1 = self.__build_Aeq1()
        Aeq2 = self.__build_Aeq2()
        Aeq3 = self.__build_Aeq3()
        Aeq4 = self.__build_Aeq4()
        self.Aeq = np.vstack([Aeq1, Aeq2, Aeq3, Aeq4])
        Aub1 = self.__build_Aub1()
        Aub2 = self.__build_Aub2()
        self.Aub = np.vstack([Aub1, Aub2])

        if solver.DEFAULT_LP_SOLVER_VARIANT == solver.CVXOPT_SOLVER_CUSTOM_ALIGN:
            from cvxopt import matrix

            self.Aeq_transf = matrix(self.Aeq.astype(np.float64))
            self.Aub_transf = matrix(self.Aub.astype(np.float64))
            self.c = matrix([1.0 * x for x in self.c])
        else:
            self.Aeq_transf = self.Aeq
            self.Aub_transf = self.Aub

    def __calculate_vectors(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates the inequality/equality vector from the knowledge of the
        initial/final marking of the synchronous product net
        """
        beq_stack = []
        bub_stack = []
        beq_stack.append(self.fin_vec - self.ini_vec)
        beq_stack.append(np.zeros(((len(self.x) - 1) * len(self.x[0]), 1)))
        beq_stack.append(np.ones((len(self.y), 1)))
        beq_stack.append(np.zeros((len(self.null_entries), 1)))
        bub_stack.append(np.zeros((len(self.x) * len(self.x[0]), 1)))
        bub_stack.append(np.zeros((len(self.y) * len(self.y[0]), 1)))
        for i in range(self.k - 1):
            bub_stack.append(self.ini_vec)

        beq = np.vstack(beq_stack)
        bub = np.vstack(bub_stack)

        return beq, bub

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
        if self.Aeq is None:
            self.__build_lin_prog_components()

        self.beq, self.bub = self.__calculate_vectors()

        if solver.DEFAULT_LP_SOLVER_VARIANT == solver.CVXOPT_SOLVER_CUSTOM_ALIGN:
            from cvxopt import matrix

            self.beq_transf = matrix(self.beq.astype(np.float64))
            self.bub_transf = matrix(self.bub.astype(np.float64))
        else:
            self.beq_transf = self.beq
            self.bub_transf = self.bub

        return self.c, self.Aub_transf, self.bub_transf, self.Aeq_transf, self.beq_transf

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
        x_vector = [0] * len(self.sync_net.transitions)
        for i in range(len(self.x)):
            for j in range(len(self.x[i])):
                x_vector[j] += sol_points[self.x[i][j]]
        for i in range(len(self.y)):
            for j in range(len(self.y[i])):
                x_vector[j] += sol_points[self.y[i][j]]
        return x_vector

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
        h = 0.0
        for i in range(len(sol_points)):
            h += sol_points[i] * self.c1[i]
        return int(h)

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

    def solve(self, variant=None) -> Tuple[int, List[int]]:
        """
        Solves the extended marking equation, returning the heuristics and the x vector

        Parameters
        -------------
        variant
            Variant of the ILP solver to use

        Returns
        -------------
        h
            Heuristics value
        x
            X vector
        """
        if variant is None:
            variant = solver.DEFAULT_LP_SOLVER_VARIANT
        # use ILP solver
        if variant is solver.CVXOPT_SOLVER_CUSTOM_ALIGN:
            variant = solver.CVXOPT_SOLVER_CUSTOM_ALIGN_ILP
        c, Aub, bub, Aeq, beq = self.get_components()
        parameters_solver = {}
        parameters_solver["use_ilp"] = True
        sol = solver.apply(c, Aub, bub, Aeq, beq, variant=variant, parameters=parameters_solver)
        sol_points = solver.get_points_from_sol(sol, variant=variant)
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
        firing_sequence, reach_fm, explained_events = align_utils.search_path_among_sol(self.sync_net, self.ini,
                                                                                        self.fin,
                                                                                        activated_transitions)
        return firing_sequence, reach_fm, explained_events


def build(trace: Trace, sync_net: PetriNet, sync_im: Marking, sync_fm: Marking,
          parameters: Optional[Dict[Any, Any]] = None) -> ExtendedMarkingEquationSolver:
    """
    Builds the extended marking equation out of a trace and a synchronous product net

    Parameters
    ---------------
    trace
        Trace
    sync_net
        Synchronous product net
    sync_im
        Initial marking (of sync net)
    sync_fm
        Final marking (of sync net)
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY => attribute to use as case identifier
        - Parameters.ACTIVITY_KEY => attribute to use as activity
        - Parameters.COSTS => (if provided) the cost function (otherwise the default cost function is applied)
        - Parameters.SPLIT_IDX => (if provided) the split points as indices of elements of the trace
            (e.g. for ["A", "B", "C", "D", "E"], specifying [1,3] as split points means splitting at "B" and "D").
            If not provided, some split points at uniform distances are found.
        - Parameters.MAX_K_VALUE => the maximum number of split points that is allowed (trim the specified indexes
            if necessary).
        - Parameters.INCIDENCE_MATRIX => (if provided) the incidence matrix associated to the sync product net
        - Parameters.A => (if provided) the A numpy matrix of the incidence matrix
        - Parameters.CONSUMPTION_MATRIX => (if provided) the consumption matrix associated to the sync product net
        - Parameters.C => (if provided) the C numpy matrix of the consumption matrix
        - Parameters.FULL_BOOTSTRAP_REQUIRED => The preset/postset of places/transitions need to be inserted
    """
    if parameters is None:
        parameters = {}

    return ExtendedMarkingEquationSolver(trace, sync_net, sync_im, sync_fm, parameters=parameters)


def get_h_value(solver: ExtendedMarkingEquationSolver, parameters: Optional[Dict[Any, Any]] = None) -> int:
    """
    Gets the heuristics value from the extended marking equation

    Parameters
    --------------
    solver
        Extended marking equation solver (class in this file)
    parameters
        Possible parameters of the algorithm
    """
    return solver.solve()[0]
