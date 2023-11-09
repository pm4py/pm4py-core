from pm4py.objects.petri_net.obj import *
from pm4py.objects.petri_net.utils import petri_utils as pn_utils

from pm4py.objects.conversion.dcr.variants.to_petri_net_submodules import utils

class SingleRelations(object):

    def __init__(self, helper_struct, mapping_exceptions) -> None:
        self.helper_struct = helper_struct
        self.mapping_exceptions = mapping_exceptions

    def create_include_pattern(self, event, event_prime, tapn) -> PetriNet:
        inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
        pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
        pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
        copy_0 = self.helper_struct[event]['transitions']
        len_copy_0 = len(copy_0)
        len_internal = len(self.helper_struct[event]['t_types'])
        len_delta = int(len_copy_0 / len_internal)
        new_transitions = []

        # copy 1
        for delta in range(len_delta):
            tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self.mapping_exceptions)
            new_transitions.extend(ts)
            for t in ts:
                tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)
        # copy 2
        if pend_place_e_prime and pend_excl_place_e_prime:
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self.mapping_exceptions)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                    pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

        # map the copy_0 last but before adding the new transitions
        # copy 0
        for t in copy_0:
            pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
            pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

        self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exclude_pattern(self, event, event_prime, tapn) -> PetriNet:
        inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
        pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
        pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
        copy_0 = self.helper_struct[event]['transitions']
        len_copy_0 = len(copy_0)
        len_internal = len(self.helper_struct[event]['t_types'])
        len_delta = int(len_copy_0 / len_internal)
        new_transitions = []

        # copy 1
        for delta in range(len_delta):
            tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self.mapping_exceptions)
            new_transitions.extend(ts)
            for t in ts:
                # check if removing t works
                tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

        # copy 2
        if pend_place_e_prime and pend_excl_place_e_prime:
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self.mapping_exceptions)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                    pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)
                    pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)

        # copy 0
        for t in copy_0:
            pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

        self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_response_pattern(self, event, event_prime, tapn) -> PetriNet:
        inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
        pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
        pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
        copy_0 = self.helper_struct[event]['transitions']
        len_copy_0 = len(copy_0)
        len_internal = len(self.helper_struct[event]['t_types'])
        len_delta = int(len_copy_0 / len_internal)
        new_transitions = []

        # copy 1
        for delta in range(len_delta):
            tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self.mapping_exceptions)
            new_transitions.extend(ts)
            for t in ts:
                tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)
        # copy 2
        if pend_excl_place_e_prime:
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self.mapping_exceptions)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                    pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

        # copy 3
        if pend_excl_place_e_prime:
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self.mapping_exceptions)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                    pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

        # copy 0
        for t in copy_0:
            pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
            pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

            pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
            pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

        self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_no_response_pattern(self, event, event_prime, tapn) -> PetriNet:
        inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
        pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
        pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
        copy_0 = self.helper_struct[event]['transitions']
        len_copy_0 = len(copy_0)
        len_internal = len(self.helper_struct[event]['t_types'])
        len_delta = int(len_copy_0 / len_internal)
        new_transitions = []

        # copy 1
        for delta in range(len_delta):
            tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self.mapping_exceptions)
            new_transitions.extend(ts)
            for t in ts:
                tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)
        # copy 2
        if pend_excl_place_e_prime:
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self.mapping_exceptions)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                    pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

        # copy 3
        if pend_excl_place_e_prime:
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self.mapping_exceptions)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                    pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

        # copy 0
        for t in copy_0:
            pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
            pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

            pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

        self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_condition_pattern(self, event, event_prime, tapn) -> PetriNet:
        inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
        exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']

        copy_0 = self.helper_struct[event]['transitions']
        len_copy_0 = len(copy_0)
        len_internal = len(self.helper_struct[event]['t_types'])
        len_delta = int(len_copy_0 / len_internal)
        new_transitions = []
        # copy 1
        if inc_place_e_prime:
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self.mapping_exceptions)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

        # copy 0
        for t in copy_0:
            pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
            pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

            pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
            pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

        self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_milestone_pattern(self, event, event_prime, tapn) -> PetriNet:
        inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
        pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']

        copy_0 = self.helper_struct[event]['transitions']
        len_copy_0 = len(copy_0)
        len_internal = len(self.helper_struct[event]['t_types'])
        len_delta = int(len_copy_0 / len_internal)
        new_transitions = []
        # copy 1
        if inc_place_e_prime:
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self.mapping_exceptions)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

        # copy 0
        for t in copy_0:
            pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
            pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

            pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

        self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn
