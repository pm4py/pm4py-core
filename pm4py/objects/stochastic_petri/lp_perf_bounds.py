from copy import copy

import numpy as np

from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.objects.petri.utils import remove_place, remove_transition, add_arc_from_to
from pm4py.objects.random_variables.exponential.random_variable import Exponential
from pm4py.util.lp import factory as lp_solver_factory
from pm4py.util.lp.util import aeq_redundant_fix

DEFAULT_REPLACEMENT_IMMEDIATE = 1000

DEFAULT_LP_SOLVER_VARIANT = lp_solver_factory.CVXOPT


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
        self.Aub = None
        self.bub = None
        self.Aeq = None
        self.beq = None
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
            variable_name = "x_" + place.name
            variable_corr = len(list(self.var_corr.keys()))
            self.var_corr[variable_name] = variable_corr
            self.inv_var_corr[variable_corr] = variable_name
        for transition in self.net.transitions:
            variable_name = "q_" + transition.name
            variable_corr = len(list(self.var_corr.keys()))
            self.var_corr[variable_name] = variable_corr
            self.inv_var_corr[variable_corr] = variable_name
        for transition in self.net.transitions:
            variable_name = "theta_" + transition.name
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
        """
        Solve the linear programming problem
        """
        target_column = self.var_corr[target_variable]

        c = [0.0] * self.variable_count
        if maximize:
            c[target_column] = -1.0
        else:
            c[target_column] = 1.0
        sol = lp_solver_factory.apply(c, self.Aub, self.bub, self.Aeq, self.beq, variant=DEFAULT_LP_SOLVER_VARIANT)
        parameters_points = {"maximize": maximize, "return_when_none": True, "var_corr": self.var_corr}

        return lp_solver_factory.get_points_from_sol(sol, parameters=parameters_points,
                                                     variant=DEFAULT_LP_SOLVER_VARIANT)

    def build_problem(self):
        """
        Build the linear programming problem
        """

        for trans in self.smap:
            rv = self.smap[trans]
            if rv.get_transition_type() == "IMMEDIATE":
                new_rv = Exponential()
                new_rv.scale = DEFAULT_REPLACEMENT_IMMEDIATE
                self.smap[trans] = new_rv
        aeq_1, beq_1, aub_1, bub_1 = self.build_1_throughput()
        aeq_2, beq_2, aub_2, bub_2 = self.build_2_flowbalance()
        aeq_3, beq_3, aub_3, bub_3 = self.build_3_secondmoment()
        aeq_4, beq_4, aub_4, bub_4 = self.build_4_populationcovariance()
        aeq_5, beq_5, aub_5, bub_5 = self.build_5_liveness()
        aeq_6, beq_6, aub_6, bub_6 = self.build_6_liveness()
        aeq_18, beq_18, aub_18, bub_18 = self.build_18_samplepath()
        aeq_19, beq_19, aub_19, bub_19 = self.build_19_samplepath()
        aeq_21, beq_21, aub_21, bub_21 = self.build_21_samplepath()
        aeq_22, beq_22, aub_22, bub_22 = self.build_22_samplepath()
        aeq_26, beq_26, aub_26, bub_26 = self.build_26_littlelaw()
        aeq_general, beq_general, aub_general, bub_general = self.build_general_cond()

        self.Aeq = np.vstack(
            (aeq_1, aeq_2, aeq_3, aeq_4, aeq_5, aeq_6, aeq_18, aeq_19, aeq_21, aeq_22, aeq_26, aeq_general))
        self.beq = np.vstack(
            (beq_1, beq_2, beq_3, beq_4, beq_5, beq_6, beq_18, beq_19, beq_21, beq_22, beq_26, beq_general))
        self.Aub = np.vstack(
            (aub_1, aub_2, aub_3, aub_4, aub_5, aub_6, aub_18, aub_19, aub_21, aub_22, aub_26, aub_general))
        self.bub = np.vstack(
            (bub_1, bub_2, bub_3, bub_4, bub_5, bub_6, bub_18, bub_19, bub_21, bub_22, bub_26, bub_general))

        self.Aeq, self.beq = aeq_redundant_fix.remove_redundant_rows(self.Aeq, self.beq)

        if DEFAULT_LP_SOLVER_VARIANT == "cvxopt":
            self.Aeq = np.transpose(self.Aeq.astype(np.float64)).tolist()
            self.beq = np.transpose(self.beq.astype(np.float64)).tolist()
            self.Aub = np.transpose(self.Aub.astype(np.float64)).tolist()
            self.bub = np.transpose(self.bub.astype(np.float64)).tolist()

    def build_1_throughput(self):
        """
        Throughput equation
        """
        aeq_1 = np.zeros((len(self.net.transitions), self.variable_count))
        beq_1 = np.zeros((len(self.net.transitions), 1))
        aub_1 = np.zeros((0, self.variable_count))
        bub_1 = np.zeros((0, 1))

        for index, transition in enumerate(self.net.transitions):
            c1 = self.var_corr["theta_" + transition.name]
            c2 = self.var_corr["q_" + transition.name]
            mu = float(self.smap[transition].get_distribution_parameters())

            aeq_1[index, c1] = 1
            aeq_1[index, c2] = -mu

        return aeq_1, beq_1, aub_1, bub_1

    def build_2_flowbalance(self):
        """
        Flow-balance equation
        """
        aeq_2 = np.zeros((len(self.net.places), self.variable_count))
        beq_2 = np.zeros((len(self.net.places), 1))
        aub_2 = np.zeros((0, self.variable_count))
        bub_2 = np.zeros((0, 1))

        for index, place in enumerate(self.net.places):
            for transition in self.presets[place].keys():
                mu = float(self.smap[transition].get_distribution_parameters())
                thetatp = self.presets[place][transition]
                c1 = self.var_corr["q_" + transition.name]
                aeq_2[index, c1] = aeq_2[index, c1] + mu * thetatp
            for transition in self.postsets[place].keys():
                mu = float(self.smap[transition].get_distribution_parameters())
                thetatp = self.postsets[place][transition]
                c2 = self.var_corr["q_" + transition.name]
                aeq_2[index, c2] = aeq_2[index, c2] - mu * thetatp

        return aeq_2, beq_2, aub_2, bub_2

    def build_3_secondmoment(self):
        """
        Second moment equation
        """
        aeq_3 = np.zeros((len(self.net.places), self.variable_count))
        beq_3 = np.zeros((len(self.net.places), 1))
        aub_3 = np.zeros((0, self.variable_count))
        bub_3 = np.zeros((0, 1))

        for index, place in enumerate(self.net.places):
            for transition in self.presets[place]:
                mu = float(self.smap[transition].get_distribution_parameters())
                w = self.presets[place][transition]
                ypt = self.var_corr["y_" + place.name + "_" + transition.name]
                qt = self.var_corr["q_" + transition.name]
                aeq_3[index, ypt] = aeq_3[index, ypt] + 2 * mu * w
                aeq_3[index, qt] = aeq_3[index, qt] + mu * w * w
                if transition in self.postsets[place]:
                    w2 = self.postsets[place][transition]
                    aeq_3[index, qt] = aeq_3[index, qt] - 2 * mu * w * w2
            for transition in self.postsets[place]:
                mu = float(self.smap[transition].get_distribution_parameters())
                w = self.postsets[place][transition]
                ypt = self.var_corr["y_" + place.name + "_" + transition.name]
                qt = self.var_corr["q_" + transition.name]
                aeq_3[index, ypt] = aeq_3[index, ypt] - 2 * mu * w
                aeq_3[index, qt] = aeq_3[index, qt] + mu * w * w
        return aeq_3, beq_3, aub_3, bub_3

    def build_4_populationcovariance(self):
        """
        Population covariance equation
        """
        aeq_4 = np.zeros((len(self.net.places) * (len(self.net.places) - 1), self.variable_count))
        beq_4 = np.zeros((len(self.net.places) * (len(self.net.places) - 1), 1))
        aub_4 = np.zeros((0, self.variable_count))
        bub_4 = np.zeros((0, 1))

        count = 0
        for p1 in self.net.places:
            for p2 in self.net.places:
                if not p1 == p2:
                    for transition in self.presets[p2]:
                        mu = float(self.smap[transition].get_distribution_parameters())
                        w = self.presets[p2][transition]
                        yp1t = self.var_corr["y_" + p1.name + "_" + transition.name]
                        aeq_4[count, yp1t] = aeq_4[count, yp1t] + mu * w
                    for transition in self.postsets[p2]:
                        mu = float(self.smap[transition].get_distribution_parameters())
                        w = self.postsets[p2][transition]
                        yp1t = self.var_corr["y_" + p1.name + "_" + transition.name]
                        aeq_4[count, yp1t] = aeq_4[count, yp1t] - mu * w
                    for transition in self.presets[p1]:
                        mu = float(self.smap[transition].get_distribution_parameters())
                        w = self.presets[p1][transition]
                        yp2t = self.var_corr["y_" + p2.name + "_" + transition.name]
                        qt = self.var_corr["q_" + transition.name]
                        aeq_4[count, yp2t] = aeq_4[count, yp2t] + mu * w
                        if transition in self.presets[p2]:
                            w2 = self.presets[p2][transition]
                            aeq_4[count, qt] = aeq_4[count, qt] + mu * w * w2
                        if transition in self.postsets[p2]:
                            w2 = self.postsets[p2][transition]
                            aeq_4[count, qt] = aeq_4[count, qt] - mu * w * w2
                    for transition in self.postsets[p1]:
                        mu = float(self.smap[transition].get_distribution_parameters())
                        w = self.postsets[p1][transition]
                        yp2t = self.var_corr["y_" + p2.name + "_" + transition.name]
                        qt = self.var_corr["q_" + transition.name]
                        aeq_4[count, yp2t] = aeq_4[count, yp2t] - mu * w
                        if transition in self.presets[p2]:
                            w2 = self.presets[p2][transition]
                            aeq_4[count, qt] = aeq_4[count, qt] - mu * w * w2
                        if transition in self.postsets[p2]:
                            w2 = self.postsets[p2][transition]
                            aeq_4[count, qt] = aeq_4[count, qt] + mu * w * w2
                    count = count + 1

        return aeq_4, beq_4, aub_4, bub_4

    def build_5_liveness(self):
        """
        Liveness equation
        """
        aeq_5 = np.zeros((0, self.variable_count))
        beq_5 = np.zeros((0, 1))
        aub_5 = np.zeros((1, self.variable_count))
        bub_5 = np.zeros((1, 1))

        for index, transition in enumerate(self.net.transitions):
            qt = self.var_corr["q_" + transition.name]
            aub_5[0, qt] = aub_5[0, qt] - 1
        bub_5[0] = -1

        return aeq_5, beq_5, aub_5, bub_5

    def build_6_liveness(self):
        """
        Liveness equation (second part)
        """
        aeq_6 = np.zeros((0, self.variable_count))
        beq_6 = np.zeros((0, 1))
        aub_6 = np.zeros((len(self.net.places), self.variable_count))
        bub_6 = np.zeros((len(self.net.places), 1))

        for index, place in enumerate(self.net.places):
            xp = self.var_corr["x_" + place.name]
            aub_6[index, xp] = aub_6[index, xp] + xp
            for trans in self.net.transitions:
                ypt = self.var_corr["y_" + place.name + "_" + trans.name]
                aub_6[index, ypt] = aub_6[index, ypt] - ypt

        return aeq_6, beq_6, aub_6, bub_6

    def build_18_samplepath(self):
        """
        Sample path condition
        """
        aeq_18 = np.zeros((0, self.variable_count))
        beq_18 = np.zeros((0, 1))
        aub_18 = np.zeros((len(self.net.transitions), self.variable_count))
        bub_18 = np.zeros((len(self.net.transitions), 1))

        for index, trans in enumerate(self.net.transitions):
            qt = self.var_corr["q_" + trans.name]
            aub_18[index, qt] = 1
            bub_18[index] = 1

        return aeq_18, beq_18, aub_18, bub_18

    def build_19_samplepath(self):
        """
        Simple path condition
        """
        aeq_19 = np.zeros((0, self.variable_count))
        beq_19 = np.zeros((0, 1))
        aub_19 = np.zeros((len(self.net.places) * len(self.net.transitions), self.variable_count))
        bub_19 = np.zeros((len(self.net.places) * len(self.net.transitions), 1))

        count = 0
        for place in self.net.places:
            xp = self.var_corr["x_" + place.name]
            for trans in self.net.transitions:
                ypt = self.var_corr["y_" + place.name + "_" + trans.name]
                aub_19[count, ypt] = 1
                aub_19[count, xp] = -1
                count = count + 1

        return aeq_19, beq_19, aub_19, bub_19

    def build_21_samplepath(self):
        count_available = 0
        for trans in self.net.transitions:
            if len(trans.in_arcs) == 1:
                count_available = count_available + 1

        aeq_21 = np.zeros((0, self.variable_count))
        beq_21 = np.zeros((0, 1))
        aub_21 = np.zeros((count_available, self.variable_count))
        bub_21 = np.zeros((count_available, 1))

        count = 0
        for trans in self.net.transitions:
            if len(trans.in_arcs) == 1:
                place = list(trans.in_arcs)[0].source
                w = self.presets[trans][place]
                ypt = self.var_corr["y_" + place.name + "_" + trans.name]
                xp = self.var_corr["x_" + place.name]
                aub_21[count, xp] = 1
                aub_21[count, ypt] = -1
                bub_21[count] = w - 1
                count = count + 1

        return aeq_21, beq_21, aub_21, bub_21

    def build_22_samplepath(self):
        count_trans_preset = 0
        for trans in self.net.transitions:
            for place in self.presets[trans]:
                count_trans_preset = count_trans_preset + 1

        aeq_22 = np.zeros((0, self.variable_count))
        beq_22 = np.zeros((0, 1))
        aub_22 = np.zeros((count_trans_preset, self.variable_count))
        bub_22 = np.zeros((count_trans_preset, 1))

        count = 0
        for trans in self.net.transitions:
            for place in self.presets[trans]:
                w = self.presets[trans][place]
                ypt = self.var_corr["y_" + place.name + "_" + trans.name]
                qt = self.var_corr["q_" + trans.name]

                aub_22[count, qt] = w
                aub_22[count, ypt] = -1
                count = count + 1

        return aeq_22, beq_22, aub_22, bub_22

    def build_26_littlelaw(self):
        """
        Little law equation
        """
        aeq_26 = np.zeros((0, self.variable_count))
        beq_26 = np.zeros((0, 1))
        aub_26 = np.zeros((len(self.net.places), self.variable_count))
        bub_26 = np.zeros((len(self.net.places), 1))

        for index, place in enumerate(self.net.places):
            xp = self.var_corr["x_" + place.name]
            summ1 = 0
            for output_trans in self.postsets[place]:
                summ1 = summ1 + float(self.smap[output_trans].get_distribution_parameters())
            aub_26[index, xp] = aub_26[index, xp] - summ1
            for input_trans in self.presets[place]:
                qt = self.var_corr["q_" + input_trans.name]
                mu = float(self.smap[input_trans].get_distribution_parameters())
                w = self.presets[place][input_trans]
                aub_26[index, qt] = aub_26[index, qt] + mu * w

        return aeq_26, beq_26, aub_26, bub_26

    def build_general_cond(self):
        """
        General conditions on the non-negativity of the variables
        """
        aeq_general = np.zeros((0, self.variable_count))
        beq_general = np.zeros((0, 1))
        aub_general = -np.eye(
            len(self.net.places) + 2 * len(self.net.transitions) + len(self.net.places) * len(self.net.transitions),
            self.variable_count)
        bub_general = np.zeros((len(self.net.places) + 2 * len(self.net.transitions) + len(self.net.places) * len(
            self.net.transitions), 1))

        return aeq_general, beq_general, aub_general, bub_general

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
        # on the copied Petri net, add a sucking transition for the final marking
        for index, place in enumerate(final_marking1):
            suck_transition = PetriNet.Transition("SUCK_TRANSITION" + str(index), None)
            net1.transitions.add(suck_transition)
            add_arc_from_to(place, suck_transition, net1)
            hidden_generator_distr = Exponential()
            hidden_generator_distr.scale = avg_time_starts
            s_map[suck_transition] = hidden_generator_distr
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
            hidden_generator_trans = PetriNet.Transition("HIDDEN_GENERATOR_TRANS" + str(index), None)
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
