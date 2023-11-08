from pm4py.objects.conversion.dcr.variants.to_petri_net_submodules.utils import Relations

class TimedPreoptimizer(object):
    need_included_place = set()
    need_executed_place = set()
    need_pending_place = set()
    need_pending_excluded_place = set()
    un_executable_events = set()

    def pre_optimize_based_on_dcr_behaviour(self, G):
        need_pending_excluded_place = set()

        inclusion_events = set()
        exclusion_events = set()

        condition_events = set()

        response_events = set()
        no_response_events = set()
        milestone_events = set()

        for event in G['events']:
            inclusion_events = inclusion_events.union(set(G['includesTo'][event] if event in G['includesTo'] else set()))
            exclusion_events = exclusion_events.union(set(G['excludesTo'][event] if event in G['excludesTo'] else set()))

            condition_events = condition_events.union(set(G['conditionsFor'][event] if event in G['conditionsFor'] else set()))

            response_events = response_events.union(set(G['responseTo'][event] if event in G['responseTo'] else set()))
            no_response_events = no_response_events.union(set(G['noResponseTo'][event] if event in G['noResponseTo'] else set()))
            milestone_events = milestone_events.union(set(G['milestonesFor'][event] if event in G['milestonesFor'] else set()))

        not_included_events = set(G['events']).difference(set(G['marking']['included']))
        not_pending_events = set(G['events']).difference(set(G['marking']['pending']))
        not_included_become_included = not_included_events.intersection(inclusion_events)
        included_become_excluded = set(G['marking']['included']).intersection(exclusion_events)
        need_included_place = not_included_become_included.union(included_become_excluded)
        unexecutable_events = not_included_events.difference(inclusion_events)

        need_executed_place = set(G['marking']['executed']).union(condition_events)
        need_pending_place = set(G['marking']['pending']).union(response_events).union(milestone_events).union(no_response_events)
        need_pending_excluded_place = need_pending_place.intersection(need_included_place)

        self.no_init_t = set(G['marking']['pending']).difference(no_response_events)
        self.no_initpend_t = not_pending_events.difference(response_events)

        self.need_included_place = need_included_place
        self.need_executed_place = need_executed_place
        self.need_pending_place = need_pending_place
        self.need_pending_excluded_place = need_pending_excluded_place
        self.un_executable_events = unexecutable_events

    def preoptimize_based_on_exceptional_cases(self,G, exceptional_cases):
        self.remove_init = set()
        self.remove_initpend = set()
        for k, values in exceptional_cases.exceptions.items():
            for v in values:
                for e in G['events']:
                    if Relations.C.value in k and Relations.M.value in k and e in v[1]:
                        if e in self.no_init_t:
                            self.remove_init.add(e)
                        if e in self.no_initpend_t:
                            self.remove_initpend.add(e)

    def remove_un_executable_events_from_dcr(self, G):

        for rule in ['conditionsFor', 'milestonesFor', 'responseTo', 'noResponseTo', 'includesTo', 'excludesTo']:
            for re in self.un_executable_events:
                G[rule].pop(re, None)
            for event in G['events']:
                if event not in self.un_executable_events and event in G[rule]:
                    G[rule][event] = G[rule][event].difference(self.un_executable_events)

        G['marking']['included'] = set(G['marking']['included']).difference(self.un_executable_events)
        G['marking']['executed'] = set(G['marking']['executed']).difference(self.un_executable_events)
        G['marking']['pending'] = set(G['marking']['pending']).difference(self.un_executable_events)
        G['events'] = set(G['events']).difference(self.un_executable_events)
        return G