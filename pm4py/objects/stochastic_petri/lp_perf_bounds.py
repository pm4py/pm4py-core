from pm4py.objects.petri.petrinet import PetriNet, Marking
from copy import copy
from pm4py.objects.petri.utils import remove_place, remove_transition, add_arc_from_to
from pm4py.objects.random_variables.exponential.random_variable import Exponential
from pm4py.objects.random_variables.random_variable import RandomVariable
import numpy as np
from scipy.optimize import linprog


class LpPerfBounds(object):
    def __init__(self, net, initial_marking, final_marking, smap, avg_time_starts):
        """
        Construct the LpPerfBounds object

        Parameters
        --------------
        net
            Petri net
        initial_marking
            Initial marking
        final_marking
            Final marking
        smap
            Stochastic map of transitions distribution
        avg_time_starts
            Average time interlapsed between case starts (may be real or provided)
        """
        self.net, self.initial_marking, self.final_marking, self.smap = self.transform_net(net, initial_marking,
                                                                                            final_marking, smap,
                                                                                            avg_time_starts)
        self.presets = {}
        self.postsets = {}
        self.var_corr = {}
        self.inv_var_corr = {}
        self.variable_count = 0

        self.build_preset_postset()
        self.build_var_corr()
        self.build_problem()
        solution = self.solve_problem("theta_decide", maximize=True)
        print(solution)

    def build_preset_postset(self):
        """
        Memorize the preset and the postset of the places/transitions of the Petri net
        """
        for place in self.net.transitions:
            self.presets[place] = {}
            self.postsets[place] = {}
            for arc in place.in_arcs:
                transition = arc.source
                self.presets[place][transition] = arc.weight
            for arc in place.out_arcs:
                transition = arc.target
                self.postsets[place][transition] = arc.weight
        for transition in self.net.places:
            self.presets[transition] = {}
            self.postsets[transition] = {}
            for arc in transition.in_arcs:
                place = arc.source
                self.presets[transition][place] = arc.weight
            for arc in transition.out_arcs:
                place = arc.target
                self.postsets[transition][place] = arc.weight

    def build_var_corr(self):
        """
        Build the correspondence between the variables of the model and the columns
        """
        variable_corr = 0
        for place in self.net.places:
            variable_name = "x_"+place.name
            variable_corr = len(list(self.var_corr.keys()))
            self.var_corr[variable_name] = variable_corr
            self.inv_var_corr[variable_corr] = variable_name
        for transition in self.net.transitions:
            variable_name = "q_"+transition.name
            variable_corr = len(list(self.var_corr.keys()))
            self.var_corr[variable_name] = variable_corr
            self.inv_var_corr[variable_corr] = variable_name
        for transition in self.net.transitions:
            variable_name = "theta_"+transition.name
            variable_corr = len(list(self.var_corr.keys()))
            self.var_corr[variable_name] = variable_corr
            self.inv_var_corr[variable_corr] = variable_name
        for place in self.net.places:
            for transition in self.net.transitions:
                variable_name = "y_" + place.name + "_" + transition.name
                variable_corr = len(list(self.var_corr.keys()))
                self.var_corr[variable_name] = variable_corr
                self.inv_var_corr[variable_corr] = variable_name
        self.variable_count = variable_corr + 1

    def solve_problem(self, target_variable, maximize=False):
        target_column = self.var_corr[target_variable]

        c = np.zeros(self.variable_count)
        if maximize:
            c[target_column] = -1
        else:
            c[target_column] = 1

        solution = linprog(c, A_ub=self.Aub, b_ub=self.bub, A_eq=self.Aeq, b_eq=self.beq)

        return solution.x[target_column]

    def build_problem(self):
        """
        Build the linear programming problem
        """
        Aeq_1, beq_1, Aub_1, bub_1 = self.build_1_throughput()
        Aeq_2, beq_2, Aub_2, bub_2 = self.build_2_flowbalance()

        self.Aeq = np.vstack((Aeq_1, Aeq_2))
        self.beq = np.vstack((beq_1, beq_2))
        self.Aub = np.vstack((Aub_1, Aub_2))
        self.bub = np.vstack((bub_1, bub_2))

    def build_1_throughput(self):
        """
        Throughput equation
        """
        Aeq_1 = np.zeros((len(self.net.transitions), self.variable_count))
        beq_1 = np.zeros((len(self.net.transitions), 1))
        Aub_1 = np.zeros((0, self.variable_count))
        bub_1 = np.zeros((0,1))

        for index, transition in enumerate(self.net.transitions):
            c1 = self.var_corr["theta_"+transition.name]
            c2 = self.var_corr["q_"+transition.name]
            mu = float(self.smap[transition].get_distribution_parameters())

            Aeq_1[index, c1] = 1
            Aeq_1[index, c2] = -mu

        return Aeq_1, beq_1, Aub_1, bub_1

    def build_2_flowbalance(self):
        """
        Flow-balance equation
        """
        Aeq_2 = np.zeros((len(self.net.places), self.variable_count))
        beq_2 = np.zeros((len(self.net.places), 1))
        Aub_2 = np.zeros((0, self.variable_count))
        bub_2 = np.zeros((0,1))

        for index, place in enumerate(self.net.places):
            for transition in self.presets[place].keys():
                mu = float(self.smap[transition].get_distribution_parameters())
                thetatp = self.presets[place][transition]
                c1 = self.var_corr["q_"+transition.name]
                Aeq_2[index, c1] = Aeq_2[index, c1] + mu * thetatp
            for transition in self.postsets[place].keys():
                mu = float(self.smap[transition].get_distribution_parameters())
                thetatp = self.postsets[place][transition]
                c2 = self.var_corr["q_"+transition.name]
                print(index, c2)
                Aeq_2[index, c2] = Aeq_2[index, c2] - mu * thetatp

        print(Aeq_2)

        return Aeq_2, beq_2, Aub_2, bub_2



    def transform_net(self, net0, initial_marking0, final_marking0, s_map, avg_time_starts):
        """
        Transform the source Petri net removing the initial and final marking, and connecting
        to each "initial" place a hidden timed transition mimicking the case start

        Parameters
        -------------
        net0
            Initial Petri net provided to the object
        initial_marking0
            Initial marking of the Petri net provided to the object
        final_marking0
            Final marking of the Petri net provided to the object
        s_map
            Stochastic map of transitions (EXPONENTIAL distribution since we assume a Markovian process)
        avg_time_starts
            Average time interlapsed between case starts

        Returns
        -------------
        net
            Petri net that will be simulated
        initial_marking
            Initial marking of the Petri net that will be simulated (empty)
        final_marking
            Final marking of the Petri net that will be simulated (empty)
        s_map
            Stochastic map of transitions enriched by new hidden case-generator transitions
        """

        # copy the Petri net object (assure that we do not change the original Petri net)
        [net1, initial_marking1, final_marking1] = copy([net0, initial_marking0, final_marking0])
        # on the copied Petri net, remove the place(s) in the final marking
        for place in final_marking1:
            net1 = remove_place(net1, place)
        # on the copied Petri net, remove both the place(s) in the initial marking and
        # the immediate transitions that are connected to it.
        target_places = []
        for place in initial_marking1:
            out_arcs = list(place.out_arcs)
            for target_arc in out_arcs:
                target_trans = target_arc.target
                if len(target_trans.in_arcs) == 1:
                    out_arcs_lev2 = list(target_trans.out_arcs)
                    for arc in out_arcs_lev2:
                        target_place = arc.target
                        target_places.append(target_place)
                    net1 = remove_transition(net1, target_trans)
            net1 = remove_place(net1, place)
        # add hidden case-generation transitions to the model.
        # all places that are left orphan by the previous operation are targeted.
        for index, place in enumerate(target_places):
            hidden_generator_trans = PetriNet.Transition("HIDDEN_GENERATOR_TRANS"+str(index), None)
            net1.transitions.add(hidden_generator_trans)
            add_arc_from_to(hidden_generator_trans, place, net1)
            hidden_generator_distr = Exponential()
            hidden_generator_distr.scale = avg_time_starts
            s_map[hidden_generator_trans] = hidden_generator_distr
        # the simulated Petri net is assumed to start from an empty initial and final marking
        initial_marking = Marking()
        final_marking = Marking()
        return net1, initial_marking, final_marking, s_map


    def get_net(self):
        """
        Get the transformed Petri net used by the simulation

        Returns
        -------------
        net
            Petri net
        initial_marking
            Initial marking
        final_marking
            Final marking
        """
        return self.net, self.initial_marking, self.final_marking