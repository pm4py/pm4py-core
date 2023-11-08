import os

from pm4py.objects.petri_net.obj import *
from pm4py.objects.petri_net.utils import petri_utils as pn_utils
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter

from pm4py.objects.conversion.dcr.variants.to_petri_net_submodules import exceptional_cases, single_relations, preoptimizer, utils


class Dcr2PetriNet(object):

    def __init__(self, preoptimize=True, postoptimize=True, map_unexecutable_events=False, debug=False) -> None:
        self.in_t_types = ['event', 'init', 'initpend', 'pend']
        self.helper_struct = {}
        self.preoptimize = preoptimize
        self.postoptimize = postoptimize
        self.map_unexecutable_events = map_unexecutable_events
        self.preoptimizer = preoptimizer.Preoptimizer()
        self.transitions = {}
        self.mapping_exceptions = None
        self.reachability_timeout = None
        self.print_steps = debug
        self.debug = debug

    def initialize_helper_struct(self, G) -> None:

        for event in G['events']:
            self.helper_struct[event] = {}
            self.helper_struct[event]['places'] = {}
            self.helper_struct[event]['places']['included'] = None
            self.helper_struct[event]['places']['pending'] = None
            self.helper_struct[event]['places']['pending_excluded'] = None
            self.helper_struct[event]['places']['executed'] = None
            self.helper_struct[event]['transitions'] = []
            self.helper_struct[event]['trans_group_index'] = 0
            self.helper_struct[event]['t_types'] = self.in_t_types

            self.transitions[event] = {}
            for event_prime in G['events']:
                self.transitions[event][event_prime] = []

    def create_event_pattern_places(self, event, G, tapn, m) -> (PetriNet, Marking):
        default_make_included = True
        default_make_pend = True
        default_make_pend_ex = True
        default_make_exec = True
        if self.preoptimize:
            default_make_included = event in self.preoptimizer.need_included_place
            default_make_pend = event in self.preoptimizer.need_pending_place
            default_make_pend_ex = event in self.preoptimizer.need_pending_excluded_place
            default_make_exec = event in self.preoptimizer.need_executed_place

        if default_make_included:
            inc_place = PetriNet.Place(f'included_{event}')
            tapn.places.add(inc_place)
            self.helper_struct[event]['places']['included'] = inc_place
            # fill the marking
            if event in G['marking']['included']:
                m[inc_place] = 1

        if default_make_pend:
            pend_place = PetriNet.Place(f'pending_{event}')
            tapn.places.add(pend_place)
            self.helper_struct[event]['places']['pending'] = pend_place
            # fill the marking
            if event in G['marking']['pending'] and event in G['marking']['included']:
                m[pend_place] = 1

        if default_make_pend_ex:
            pend_excl_place = PetriNet.Place(f'pending_excluded_{event}')
            tapn.places.add(pend_excl_place)
            self.helper_struct[event]['places']['pending_excluded'] = pend_excl_place
            # fill the marking
            if event in G['marking']['pending'] and not event in G['marking']['included']:
                m[pend_excl_place] = 1

        if default_make_exec:
            exec_place = PetriNet.Place(f'executed_{event}')
            tapn.places.add(exec_place)
            self.helper_struct[event]['places']['executed'] = exec_place
            # fill the marking
            if event in G['marking']['executed']:
                m[exec_place] = 1
        if self.preoptimize:
            ts = ['event']
            if default_make_exec and not event in G['marking']['executed'] and not event in self.preoptimizer.no_init_t:
                ts.append('init')
            if default_make_exec and default_make_pend and not event in self.preoptimizer.no_initpend_t:
                ts.append('initpend')
            if default_make_pend:
                ts.append('pend')
            self.helper_struct[event]['t_types'] = ts

        return tapn, m

    def create_event_pattern(self, event, G, tapn, m) -> (PetriNet, Marking):
        tapn, m = self.create_event_pattern_places(event, G, tapn, m)
        tapn, ts = utils.create_event_pattern_transitions_and_arcs(tapn, event, self.helper_struct,
                                                                             self.mapping_exceptions)
        self.helper_struct[event]['transitions'].extend(ts)
        return tapn, m

    def post_optimize_petri_net_reachability_graph(self, tapn, m, G=None) -> PetriNet:
        from pm4py.objects.petri_net.utils import reachability_graph
        # from pm4py.visualization.transition_system import visualizer as ts_visualizer
        from pm4py.objects.petri_net.transport_invariant import semantics as tapn_semantics
        max_elab_time = 2 * 60 * 60  # 2 hours
        if self.reachability_timeout:
            max_elab_time = self.reachability_timeout
        trans_sys = reachability_graph.construct_reachability_graph(tapn, m, use_trans_name=True,
                        parameters={
                            'petri_semantics': tapn_semantics.TransportInvariantSemantics(),
                            'max_elab_time': max_elab_time
                        })

        fired_transitions = set()

        for transition in trans_sys.transitions:
            fired_transitions.add(transition.name)

        ts_to_remove = set()
        for t in tapn.transitions:
            if t.name not in fired_transitions:
                ts_to_remove.add(t)
        for t in ts_to_remove:
            tapn = pn_utils.remove_transition(tapn, t)

        changed_places = set()
        for state_list in trans_sys.states:
            for state in state_list.name:
                changed_places.add(state)

        parallel_places = set()
        # places_to_rename = {}
        ps_to_remove = tapn.places.difference(changed_places)
        # if G:
        #     for event in G['events']:
        #         for type, event_place in self.helper_struct[event]['places'].items():
        #             for type_prime, event_place_prime in self.helper_struct[event]['places'].items():
        #                 if event_place and event_place_prime and event_place.name != event_place_prime.name and \
        #                         event_place not in parallel_places:
        #                     is_parallel = False
        #                     ep_ins = event_place.in_arcs
        #                     epp_ins = event_place_prime.in_arcs
        #                     ep_outs = event_place.out_arcs
        #                     epp_outs = event_place_prime.out_arcs
        #                     if len(ep_ins) == len(epp_ins) and len(ep_outs) == len(epp_outs):
        #                         ep_sources = set()
        #                         epp_sources = set()
        #                         for ep_in in ep_ins:
        #                             ep_sources.add(ep_in.source)
        #                         for epp_in in epp_ins:
        #                             epp_sources.add(epp_in.source)
        #                         ep_targets = set()
        #                         epp_targets = set()
        #                         for ep_out in ep_outs:
        #                             ep_targets.add(ep_out.target)
        #                         for epp_out in epp_outs:
        #                             epp_targets.add(epp_out.target)
        #                         if ep_sources == epp_sources and ep_targets == epp_targets:
        #                             is_parallel = True
        #                     if is_parallel and m[event_place] == m[event_place_prime]:
        #                         parallel_places.add(event_place_prime)
        #                         places_to_rename[event_place] = f'{type_prime}_{event_place.name}'
        ps_to_remove = ps_to_remove.union(parallel_places)
        for p in ps_to_remove:
            tapn = pn_utils.remove_place(tapn, p)

        # for p, name in places_to_rename.items():
        #     p.name = name

        return tapn

    def export_debug_net(self, tapn, m, path, step, pn_export_format):
        path_without_extension, extens = os.path.splitext(path)
        debug_save_path = f'{path_without_extension}_{step}{extens}'
        pnml_exporter.apply(tapn, m, debug_save_path, variant=pn_export_format, parameters={'isTimed': self.timed})

    def dcr2tapn(self, G, tapn_path) -> (PetriNet, Marking):
        self.basic = True  # True (basic) = inc,ex,resp,cond | False = basic + no-resp,mil
        self.timed = False  # False = untimed | True = timed cond (delay) and resp (deadline)
        self.initialize_helper_struct(G)
        self.mapping_exceptions = exceptional_cases.ExceptionalCases(self.helper_struct)
        self.preoptimizer = preoptimizer.Preoptimizer()
        induction_step = 0
        pn_export_format = pnml_exporter.TAPN
        if tapn_path.endswith("pnml"):
            pn_export_format = pnml_exporter.PNML

        tapn = PetriNet("Dcr2Tapn")
        m = Marking()
        # pre-optimize mapping based on DCR graph behaviour
        if self.preoptimize:
            if self.print_steps:
                print('[i] preoptimizing')
            self.preoptimizer.pre_optimize_based_on_dcr_behaviour(G)
            if not self.map_unexecutable_events:
                G = self.preoptimizer.remove_un_executable_events_from_dcr(G)

        # including the handling of exception cases from the induction step
        G_old = deepcopy(G)
        G = self.mapping_exceptions.filter_exceptional_cases(G)
        if self.preoptimize:
            if self.print_steps:
                print('[i] finding exceptional behaviour')
            self.preoptimizer.preoptimize_based_on_exceptional_cases(G, self.mapping_exceptions)

        # map events
        if self.print_steps:
            print('[i] mapping events')
        for event in G['events']:
            tapn, m = self.create_event_pattern(event, G, tapn, m)

        if self.debug:
            self.export_debug_net(tapn, m, tapn_path, f'{induction_step}event', pn_export_format)
            induction_step += 1
        # all self exceptions have been mapped at this point

        sr = single_relations.SingleRelations(self.helper_struct, self.mapping_exceptions)
        # map constraining relations
        if self.print_steps:
            print('[i] map constraining relations')
        for event in G['conditionsFor']:
            for event_prime in G['conditionsFor'][event]:
                tapn = sr.create_condition_pattern(event, event_prime, tapn)
                if self.debug:
                    self.export_debug_net(tapn, m, tapn_path, f'{induction_step}conditionsFor', pn_export_format)
                    induction_step += 1
        if not self.basic:
            for event in G['milestonesFor']:
                for event_prime in G['milestonesFor'][event]:
                    tapn = sr.create_milestone_pattern(event, event_prime, tapn)
                    if self.debug:
                        self.export_debug_net(tapn, m, tapn_path, f'{induction_step}milestonesFor', pn_export_format)
                        induction_step += 1

        # map effect relations
        if self.print_steps:
            print('[i] map effect relations')
        for event in G['includesTo']:
            for event_prime in G['includesTo'][event]:
                tapn = sr.create_include_pattern(event, event_prime, tapn)
                if self.debug:
                    self.export_debug_net(tapn, m, tapn_path, f'{induction_step}includesTo', pn_export_format)
                    induction_step += 1
        for event in G['excludesTo']:
            for event_prime in G['excludesTo'][event]:
                tapn = sr.create_exclude_pattern(event, event_prime, tapn)
                if self.debug:
                    self.export_debug_net(tapn, m, tapn_path, f'{induction_step}{event}excludesTo{event_prime}', pn_export_format)
                    induction_step += 1
        for event in G['responseTo']:
            for event_prime in G['responseTo'][event]:
                tapn = sr.create_response_pattern(event, event_prime, tapn)
                if self.debug:
                    self.export_debug_net(tapn, m, tapn_path, f'{induction_step}responseTo', pn_export_format)
                    induction_step += 1
        if not self.basic:
            for event in G['noResponseTo']:
                for event_prime in G['noResponseTo'][event]:
                    tapn = sr.create_no_response_pattern(event, event_prime, tapn)
                    if self.debug:
                        self.export_debug_net(tapn, m, tapn_path, f'{induction_step}noResponseTo', pn_export_format)
                        induction_step += 1

        # handle all relation exceptions
        if self.print_steps:
            print('[i] handle all relation exceptions')
        tapn = self.mapping_exceptions.map_exceptional_cases_between_events(tapn, m)

        if self.debug:
            self.export_debug_net(tapn, m, tapn_path, f'{induction_step}exceptions', pn_export_format)
            induction_step += 1

        # post-optimize based on the petri net reachability graph
        if self.postoptimize:
            if self.print_steps:
                print('[i] post optimizing')
            tapn = self.post_optimize_petri_net_reachability_graph(tapn, m, G)

        if self.print_steps:
            print(f'[i] export to {tapn_path}')

        pnml_exporter.apply(tapn, m, tapn_path, variant=pn_export_format, parameters={'isTimed': self.timed})

        return tapn, m


def run_specific_dcr():
    '''
    here you can write your own graph and run it
    '''
    dcr = {
        'events': {'Triage', 'RelA', 'Reg', 'RelB','CRP'},
        'conditionsFor': {'RelA': {'Triage','Reg','RelB'}, 'RelB': {'CRP'}},
        'milestonesFor': {},
        'responseTo': {},
        'noResponseTo': {},
        'includesTo': {},
        'excludesTo': {'Reg': {'Reg'},'RelB': {'RelB'}, 'RelA': {'RelA', 'RelB', 'Triage'}},
        'marking': {'executed': set(),
                    'included': {'Triage', 'RelA', 'Reg', 'RelB','CRP'},
                    'pending': set()
                    }
    }

    d2p = Dcr2PetriNet(preoptimize=True, postoptimize=True, map_unexecutable_events=False)
    print('[i] dcr')
    tapn, m = d2p.dcr2tapn(dcr, tapn_path="/home/vco/Projects/pm4py-dcr/models/one_petri_test.tapn")

def clean_input(dcr, white_space_replacement=None):
    if white_space_replacement is None:
        white_space_replacement = ''
    # remove all space characters and put conditions and milestones in the correct order (according to the actual arrows)
    for k, v in deepcopy(dcr).items():
        if k in ['includesTo', 'excludesTo', 'conditionsFor', 'responseTo', 'milestonesFor', 'noResponseTo']:
            v_new = {}
            for k2, v2 in v.items():
                v_new[k2.strip().replace(' ', white_space_replacement)] = set([v3.strip().replace(' ', white_space_replacement) for v3 in v2])
            dcr[k] = v_new
        elif k in ['conditionsForDelays', 'responseToDeadlines']:
            v_new = {}
            for k2, v2 in v.items():
                v_new[k2.strip().replace(' ', white_space_replacement)] = set([(v3.strip().replace(' ', white_space_replacement),d) for (v3,d) in v2])
            dcr[k] = v_new
        elif k == 'marking':
            for k2 in ['executed', 'included', 'pending']:
                new_v = set([v2.strip().replace(' ', white_space_replacement) for v2 in dcr[k][k2]])
                dcr[k][k2] = new_v
        elif k in ['subprocesses', 'nestings', 'labelMapping', 'roleAssignments', 'readRoleAssignments']:
            v_new = {}
            for k2, v2 in v.items():
                v_new[k2.strip().replace(' ', white_space_replacement)] = set([v3.strip().replace(' ', white_space_replacement) for v3 in v2])
            dcr[k] = v_new
        else:
            new_v = set([v2.strip().replace(' ', white_space_replacement) for v2 in dcr[k]])
            dcr[k] = new_v
    return dcr


if __name__ == "__main__":
    # run_specific_dcr()
    import pm4py
    from pm4py.algo.discovery.dcr_discover import algorithm as dcr_discover
    from pm4py.objects.dcr.exporter import exporter as dcr_exporter

    # dcr = {
    #     'events': {'A', 'B', 'C'},
    #     'conditionsFor': {'B': {'A'}},
    #     'milestonesFor': {},
    #     'responseTo': {},
    #     'noResponseTo': {},
    #     'includesTo': {},
    #     'excludesTo': {'B': {'A', 'B', 'C'}, 'A': {'A', 'B', 'C'}, 'C': {'A','B','C'}},
    #     'conditionsForDelays': {},
    #     'responseToDeadlines': {},
    #     'marking': {'executed': {},
    #                 'included': {'A', 'B', 'C'},
    #                 'pending': {},
    #                 'pendingDeadline': {}
    #                 }
    # }

    sepsis_log = pm4py.read_xes('/home/vco/Datasets/Sepsis Cases - Event Log.xes', return_legacy_log_object=True)
    dcr_sepsis, _ = dcr_discover.apply(sepsis_log)
    dcr_sepsis = clean_input(dcr_sepsis, '')
    path = '/home/vco/Projects/pm4py-dcr/models/'
    dcr_exporter.apply(dcr_sepsis, path+'sepsis.xml')
    d2p = Dcr2PetriNet(preoptimize=True, postoptimize=True, map_unexecutable_events=False, debug=False)
    file_name = 'sepsis.tapn'
    d2p.print_steps = True
    tapn = d2p.dcr2tapn(dcr_sepsis, path+file_name)
    # file_name = 'me.tapn'
    # tapn = d2p.dcr2tapn(dcr, path+file_name)