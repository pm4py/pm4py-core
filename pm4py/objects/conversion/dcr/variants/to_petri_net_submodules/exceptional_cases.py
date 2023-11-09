from pm4py.objects.petri_net.obj import *
from pm4py.objects.petri_net.utils import petri_utils as pn_utils
from pm4py.objects.dcr.obj import Relations
from pm4py.objects.conversion.dcr.variants.to_petri_net_submodules import utils

from itertools import combinations

I = Relations.I.value
E = Relations.E.value
R = Relations.R.value
N = Relations.N.value
C = Relations.C.value
M = Relations.M.value


class ExceptionalCases(object):

    def __init__(self, helper_struct) -> None:
        self.helper_struct = helper_struct

        self.effect_relations = [I, E, R, N]
        self.constrain_relations = [C, M]
        self.all_relations = self.effect_relations + self.constrain_relations

        self.self_exceptions = {}
        for r in self.all_relations:
            self.self_exceptions[r] = set()
        self.self_exceptions[frozenset([E, R])] = set()
        self.self_exceptions[frozenset([C, M])] = set()
        self.exceptions = {}
        self.apply_exceptions = {}
        for i in range(6, 1, -1):
            for comb in combinations(self.all_relations, i):
                self.exceptions[frozenset(comb)] = set()
                apply_comb = set(comb)
                if I in apply_comb and E in apply_comb:
                    apply_comb.remove(E)
                if R in apply_comb and N in apply_comb:
                    apply_comb.remove(N)
                self.apply_exceptions[frozenset(apply_comb)] = None

        # 2 constrain + 4 effect relations (permutations 1 - 1 [because {CMIERN}=={CMIR}]) = 0
        # 2 constrain + 3 effect relations (permutations 4 - 4 [all reduce to 2 constrain 2 effects]) = 0
        # 2 constrain + 2 effect relations (permutations 6 - 2 [{CMIE}=={CMI} and {CMRN}=={CMR}]) = 4
        self.apply_exceptions[
            frozenset([C, M, E, R])] = self.create_exception_condition_milestone_exclude_response_pattern
        self.apply_exceptions[
            frozenset([C, M, E, N])] = self.create_exception_condition_milestone_exclude_no_response_pattern
        self.apply_exceptions[
            frozenset([C, M, I, R])] = self.create_exception_condition_milestone_include_response_pattern
        self.apply_exceptions[
            frozenset([C, M, I, N])] = self.create_exception_condition_milestone_include_no_response_pattern
        # 1 constrain + 4 effect relations (permutations 2 - 2 [all reduce to 1 constrain 2 effects]) = 0
        # 1 constrain + 3 effect relations (permutations 8 - 8 [all reduce to 1 constrain 2 effects]) = 0
        # 0 constrain + 4 effect relations (1-1 [because {I,E,R,N}=={I,R}]) = 0
        # 2 constrain + 1 effect (4)
        self.apply_exceptions[frozenset([C, M, R])] = self.create_exception_condition_milestone_response_pattern
        self.apply_exceptions[frozenset([C, M, N])] = self.create_exception_condition_milestone_no_response_pattern
        self.apply_exceptions[frozenset([C, M, I])] = self.create_exception_condition_milestone_include_pattern
        self.apply_exceptions[frozenset([C, M, E])] = self.create_exception_condition_milestone_exclude_pattern
        # 1 constrain + 2 effect relations (12 - 4 [{C,R,N},{C,I,E},{M,R,N},{M,I,E}]) = 8
        self.apply_exceptions[frozenset([M, N, I])] = self.create_exception_milestone_no_response_include_pattern
        self.apply_exceptions[frozenset([M, N, E])] = self.create_exception_milestone_no_response_exclude_pattern
        self.apply_exceptions[frozenset([M, R, I])] = self.create_exception_milestone_response_include_pattern
        self.apply_exceptions[frozenset([M, R, E])] = self.create_exception_milestone_response_exclude_pattern
        self.apply_exceptions[frozenset([C, N, I])] = self.create_exception_condition_no_response_include_pattern
        self.apply_exceptions[frozenset([C, N, E])] = self.create_exception_condition_no_response_exclude_pattern
        self.apply_exceptions[frozenset([C, R, I])] = self.create_exception_condition_response_include_pattern
        self.apply_exceptions[frozenset([C, R, E])] = self.create_exception_condition_response_exclude_pattern
        # 0 constrain + 3 effect relations (4 - 4 [all reduce to 2 effects]) = 0
        # 1 constrain + 1 effect relation (8) = 8
        self.apply_exceptions[frozenset([I, C])] = self.create_exception_condition_include_pattern
        self.apply_exceptions[frozenset([E, C])] = self.create_exception_condition_exclude_pattern
        self.apply_exceptions[frozenset([R, C])] = self.create_exception_condition_response_pattern
        self.apply_exceptions[frozenset([C, N])] = self.create_exception_condition_no_response_pattern
        self.apply_exceptions[frozenset([M, N])] = self.create_exception_milestone_no_response_pattern
        self.apply_exceptions[frozenset([M, E])] = self.create_exception_milestone_exclude_pattern
        self.apply_exceptions[frozenset([M, I])] = self.create_exception_milestone_include_pattern
        self.apply_exceptions[frozenset([M, R])] = self.create_exception_milestone_response_pattern
        # 0 constrain + 2 effect relations (6 - 2 [{R,N},{I,E}]) = 4
        self.apply_exceptions[frozenset([I, R])] = self.create_exception_response_include_pattern
        self.apply_exceptions[frozenset([E, R])] = self.create_exception_response_exclude_pattern
        self.apply_exceptions[frozenset([N, E])] = self.create_exception_no_response_exclude_pattern
        self.apply_exceptions[frozenset([N, I])] = self.create_exception_no_response_include_pattern
        # 2 constrain + 0 effect relations (1) = 1
        self.apply_exceptions[frozenset([C, M])] = self.create_exception_condition_milestone_pattern

    def filter_exceptional_cases(self, G):
        for e in G['events']:
            for e_prime in G['events']:
                if e == e_prime:
                    # same event multiple self relations
                    if (e in G['responseTo'] and e_prime in G['responseTo'][e]) and (
                            e in G['excludesTo'] and e_prime in G['excludesTo'][e]) and \
                            (e in G['conditionsFor'] and e_prime in G['conditionsFor'][e]) and (
                            e in G['milestonesFor'] and e_prime in G['milestonesFor'][e]) and \
                            (e in G['includesTo'] and e_prime in G['includesTo'][e]) and (
                            e in G['noResponseTo'] and e_prime in G['noResponseTo'][e]):
                        G['conditionsFor'][e].remove(e_prime)
                        G['milestonesFor'][e].remove(e_prime)
                        G['responseTo'][e].remove(e_prime)
                        G['excludesTo'][e].remove(e_prime)
                        G['includesTo'][e].remove(e_prime)
                        G['noResponseTo'][e].remove(e_prime)
                        self.helper_struct[e]['t_types'] = ['event']
                        self.self_exceptions['responseTo'].add(e)
                        self.self_exceptions[frozenset(['conditionsFor', 'milestonesFor'])].add(e)

                    if (e in G['responseTo'] and e_prime in G['responseTo'][e]) and (
                            e in G['excludesTo'] and e_prime in G['excludesTo'][e]):
                        G['responseTo'][e].remove(e_prime)
                        G['excludesTo'][e].remove(e_prime)
                        self.self_exceptions[frozenset(['excludesTo', 'responseTo'])].add(e)
                    if (e in G['conditionsFor'] and e_prime in G['conditionsFor'][e]) and (
                            e in G['milestonesFor'] and e_prime in G['milestonesFor'][e]):
                        G['conditionsFor'][e].remove(e_prime)
                        G['milestonesFor'][e].remove(e_prime)
                        self.helper_struct[e]['t_types'] = ['event']
                        self.self_exceptions[frozenset(['conditionsFor', 'milestonesFor'])].add(e)
                    if (e in G['includesTo'] and e_prime in G['includesTo'][e]) and (
                            e in G['excludesTo'] and e_prime in G['excludesTo'][e]):
                        G['excludesTo'][e].remove(e_prime)
                    # same event one self relation
                    for rel in self.all_relations:
                        if e in G[rel] and e_prime in G[rel][e]:
                            G[rel][e].remove(e_prime)
                            self.self_exceptions[rel].add(e)
                            match rel:
                                case 'conditionsFor':
                                    # removes the creation of the init and initpend transitions
                                    self.helper_struct[e]['t_types'] = ['event', 'pend']
                                case 'milestonesFor':
                                    # removes the creation of the pend and initpend transitions
                                    self.helper_struct[e]['t_types'] = ['event', 'init']
                else:
                    # distinct events
                    for exception in self.exceptions.keys():
                        has_multiple_rel = True
                        for rel in exception:
                            has_multiple_rel = has_multiple_rel and (e in G[rel] and e_prime in G[rel][e])
                        if has_multiple_rel:
                            remove_from_g = True
                            if I in exception and E in exception:
                                G[E][e].remove(e_prime)
                                remove_from_g = False
                            if R in exception and N in exception:
                                G[N][e].remove(e_prime)
                                remove_from_g = False
                            if remove_from_g:
                                self.exceptions[exception].add((e, e_prime))
                                for rel in exception:
                                    G[rel][e].remove(e_prime)

        return G

    def map_exceptional_cases_between_events(self, tapn, m=None) -> PetriNet:
        for exception, pairs in self.exceptions.items():
            if len(pairs) > 0:
                tapn = self.apply_exceptions[exception](tapn, m)
        return tapn

    def create_exception_condition_milestone_exclude_response_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([E, R, C, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1 and 2
            copies = [1, 2] if pend_excl_place_e_prime else [1]
            for i in copies:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)
                        if i == 1:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')
                        elif i == 2:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_milestone_exclude_no_response_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([E, N, C, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1 and 2
            copies = [1, 2] if pend_excl_place_e_prime else [1]
            for i in copies:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        if i == 1:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')
                        elif i == 2:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_milestone_include_response_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([I, R, C, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1 and 2
            copies = [1, 2] if pend_excl_place_e_prime else [1]
            for i in copies:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                        if i == 1:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')
                        elif i == 2:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_milestone_include_no_response_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([I, N, C, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1 and 2
            copies = [1, 2] if pend_excl_place_e_prime else [1]
            for i in copies:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        if i == 1:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')
                        elif i == 2:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_milestone_response_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([R, C, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1 and 2
            copies = [1, 2] if pend_excl_place_e_prime else [1]
            for i in copies:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)
                        if i == 1:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')
                        elif i == 2:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_milestone_no_response_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([N, C, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1 and 2
            copies = [1, 2] if pend_excl_place_e_prime else [1]
            for i in copies:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        if i == 1:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')
                        elif i == 2:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_milestone_include_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([I, C, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1 and 2
            copies = [1, 2] if pend_excl_place_e_prime else [1]
            for i in copies:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        if i == 1:
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')
                        elif i == 2:
                            pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                            pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_milestone_exclude_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([E, C, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1
            if inc_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_milestone_no_response_include_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([I, N, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []

            # copy 1
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

            # copy 2
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            if pend_place_e_prime:
                for t in copy_0:
                    pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                    pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_milestone_no_response_exclude_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([E, N, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []

            # copy 1
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

            # copy 2
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            if pend_place_e_prime:
                for t in copy_0:
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                    pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_milestone_response_include_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([I, R, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excluded_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1
            if inc_place_e_prime and pend_excluded_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)

                        pn_utils.add_arc_from_to(pend_excluded_place_e_prime, t, tapn, type='inhibitor')

            # copy 2
            if inc_place_e_prime and pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)

            # copy 0
            if pend_excluded_place_e_prime:
                for t in copy_0:
                    pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                    pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(pend_excluded_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_milestone_response_exclude_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([E, R, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excluded_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1
            if inc_place_e_prime and pend_excluded_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excluded_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, pend_excluded_place_e_prime, tapn)

            # copy 2
            if inc_place_e_prime and pend_excluded_place_e_prime and pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excluded_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, pend_excluded_place_e_prime, tapn)

            # copy 0
            if pend_excluded_place_e_prime:
                for t in copy_0:
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                    pn_utils.add_arc_from_to(t, pend_excluded_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(pend_excluded_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_no_response_include_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([N, C, I])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []

            # copy 1
            if pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            # copy 2
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

            # copy 3
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            if pend_place_e_prime:
                for t in copy_0:
                    pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                    pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                    pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_no_response_exclude_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([N, C, E])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []

            # copy 1
            if pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            # copy 2
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

            # copy 3
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            if pend_place_e_prime:
                for t in copy_0:
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                    pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                    pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_response_include_pattern(self, tapn, m=None) -> PetriNet:
        '''
        TODO: Make the if places statements
        :param tapn:
        :param m:
        :return:
        '''
        for (event, event_prime) in self.exceptions[frozenset([I, R, C])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                    pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

                    pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)

            # copy 2
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                    pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)

                    pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 3
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                    pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)

                    pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                    pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')
            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_response_exclude_pattern(self, tapn, m=None) -> PetriNet:
        '''
        TODO: Make the if places statements
        :param tapn:
        :param m:
        :return:
        '''
        for (event, event_prime) in self.exceptions[frozenset([E, R, C])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                    pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

                    pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)
                    pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)
            # copy 2
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                    pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')
                    pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)

            # copy 3
            for delta in range(len_delta):
                tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                new_transitions.extend(ts)
                for t in ts:
                    tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                    pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                    pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)
                    pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')
                pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_include_pattern(self, tapn, m=None) -> PetriNet:
        '''
        TODO: Test the if places statements
        :param tapn:
        :param m:
        :return:
        '''
        for (event, event_prime) in self.exceptions[frozenset([I, C])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []

            # copy 1
            if pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct,
                                                                              self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)

                        pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 2
            if inc_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_exclude_pattern(self, tapn, m=None) -> PetriNet:
        '''
        TODO: Test the if places statements
        :param tapn:
        :param m:
        :return:
        '''
        for (event, event_prime) in self.exceptions[frozenset([E, C])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []

            # copy 1
            if pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)
                        pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)

            # copy 2
            if inc_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_response_pattern(self, tapn, m=None) -> PetriNet:
        '''
        Done
        :param tapn:
        :param m:
        :return:
        '''
        for (event, event_prime) in self.exceptions[frozenset([R, C])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []

            # copy 1
            if pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)
                        pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)

            # copy 2
            if inc_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)

            # copy 3
            if pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)
                        pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')
                pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_response_include_pattern(self, tapn, m=None) -> PetriNet:
        '''
        DONE
        :param tapn:
        :param m:
        :return:
        '''
        for (event, event_prime) in self.exceptions[frozenset([I, R])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []

            # copy 1
            if pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)
            # copy 2
            if inc_place_e_prime and pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)

                        pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

            # copy 3
            if pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)

                        pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_response_exclude_pattern(self, tapn, m=None) -> PetriNet:
        '''
        DONE
        :param tapn:
        :param m:
        :return:
        '''
        for (event, event_prime) in self.exceptions[frozenset([E, R])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1
            if pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)
                        pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)
            # copy 2
            if pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

            # copy 3
            if pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                pn_utils.add_arc_from_to(t, pend_excl_place_e_prime, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_condition_no_response_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([N, C])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []

            # copy 1
            if pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            # copy 2
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

            # copy 3
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
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

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_no_response_exclude_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([E, N])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []

            # copy 1
            if pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)
            # copy 2
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

            # copy 3
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_no_response_include_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([I, N])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []

            # copy 1
            if inc_place_e_prime and pend_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)

                        pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn)
            # copy 2
            if inc_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

            # copy 3
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_milestone_no_response_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([N, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []

            # copy 1
            if inc_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn, type='inhibitor')

            # copy 2
            if inc_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
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

    def create_exception_condition_milestone_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([C, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            exec_place_e_prime = self.helper_struct[event_prime]['places']['executed']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1
            if inc_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

                pn_utils.add_arc_from_to(t, exec_place_e_prime, tapn)
                pn_utils.add_arc_from_to(exec_place_e_prime, t, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_milestone_exclude_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([E, M])]:
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
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_milestone_include_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([I, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excl_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']
            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1
            if pend_place_e_prime and pend_excl_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)
                        pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(pend_excl_place_e_prime, t, tapn)
            # copy 2
            if inc_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
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

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn

    def create_exception_milestone_response_pattern(self, tapn, m=None) -> PetriNet:
        for (event, event_prime) in self.exceptions[frozenset([R, M])]:
            inc_place_e_prime = self.helper_struct[event_prime]['places']['included']
            pend_place_e_prime = self.helper_struct[event_prime]['places']['pending']
            pend_excluded_place_e_prime = self.helper_struct[event_prime]['places']['pending_excluded']

            copy_0 = self.helper_struct[event]['transitions']
            len_copy_0 = len(copy_0)
            len_internal = len(self.helper_struct[event]['t_types'])
            len_delta = int(len_copy_0 / len_internal)
            new_transitions = []
            # copy 1
            if pend_excluded_place_e_prime or inc_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(pend_excluded_place_e_prime, t, tapn, type='inhibitor')
                        pn_utils.add_arc_from_to(t, pend_excluded_place_e_prime, tapn)

            # copy 2
            if pend_excluded_place_e_prime and inc_place_e_prime:
                for delta in range(len_delta):
                    tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct, self)
                    new_transitions.extend(ts)
                    for t in ts:
                        tapn, t = utils.map_existing_transitions_of_copy_0(delta*len_internal, copy_0, t, tapn)

                        pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn, type='inhibitor')

                        pn_utils.add_arc_from_to(t, pend_excluded_place_e_prime, tapn)
                        pn_utils.add_arc_from_to(pend_excluded_place_e_prime, t, tapn)

            # copy 0
            for t in copy_0:
                pn_utils.add_arc_from_to(t, inc_place_e_prime, tapn)
                pn_utils.add_arc_from_to(inc_place_e_prime, t, tapn)

                pn_utils.add_arc_from_to(pend_place_e_prime, t, tapn, type='inhibitor')
                pn_utils.add_arc_from_to(t, pend_place_e_prime, tapn)

            self.helper_struct[event]['transitions'].extend(new_transitions)
        return tapn
