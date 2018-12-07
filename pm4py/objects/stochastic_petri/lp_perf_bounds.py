from pm4py.objects.petri.petrinet import PetriNet, Marking
from copy import copy
from pm4py.objects.petri.utils import remove_place, remove_transition, add_arc_from_to
from pm4py.objects.random_variables.exponential.random_variable import Exponential
from pm4py.objects.random_variables.random_variable import RandomVariable


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