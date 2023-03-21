from copy import deepcopy
from pm4py import get_event_attribute_values
import pm4py
from pm4py.algo.discovery.dcr_discover import algorithm as alg

from pm4py.objects.dcr import semantics as dcr_semantics


def apply_mutual_exclusion(log, findAdditionalConditions=True, discardSelfInPredecessors=True, **kwargs):
    event_log = log
    basic_dcr = alg.apply(event_log, alg.DCR_BASIC, findAdditionalConditions=findAdditionalConditions)
    cluster_dict = {}

    # for event in basic_dcr['events']:
    #     if event in basic_dcr['excludesTo'] and event in basic_dcr['excludesTo'][event]:
    #         basic_dcr['excludesTo'][event].discard(event)

    keys = sorted(basic_dcr['excludesTo'].keys())
    for k in keys:
        preds_set = frozenset(sorted(basic_dcr['excludesTo'][k]))
        if preds_set in cluster_dict.keys():
            cluster_dict[preds_set].add(k)
        else:
            cluster_dict[preds_set] = set([k])

    subprocesses = {}
    subprocess_notation = 'S'
    i = 0
    for k, v in cluster_dict.items():
        if len(v) > 1:
            subprocesses[f'{subprocess_notation}{i}'] = frozenset(v)
            i = i + 1
    # now mine the dcr graph inside the subprocess
    sp_dcr_dict = {}
    for name, subprocess in subprocesses.items():
        sp_dcr_dict[name] = {'events': subprocess,
                             'conditionsFor': {},
                             'milestonesFor': {},
                             'responseTo': {},
                             'includesTo': {},
                             'excludesTo': {},
                             'marking': {'included': subprocess,
                                         'pending': set(),
                                         'executed': set()}
                             }
        # subset_log = subprocess_event_log[subprocess_event_log['concept:name'].isin(subprocess)]
        # subprocess_dcr[name] = alg.apply(subset_log, alg.DCR_BASIC, findAdditionalConditions=findAdditionalConditions)

    # now replay inside the dcr graph and replace with a subprocess
    subprocess_log = pm4py.objects.log.obj.EventLog()
    trace: pm4py.objects.log.obj.Trace
    event: pm4py.objects.log.obj.Event
    for trace in event_log:
        # only replace with the subprocess when the subprocess is accepting
        sp_trace = pm4py.objects.log.obj.Trace()
        for event in trace:
            # set all subprocess dcr graphs to their initial state
            sp_dcr_instance = deepcopy(sp_dcr_dict)
            sp_event = None
            for name, sp in subprocesses.items():
                if event['concept:name'] in sp:
                    # if the event is in the subprocess then execute it within the subprocess model
                    executed = dcr_semantics.execute(event['concept:name'],
                                                     sp_dcr_instance[name])  # TODO: check if it always executes
                    accepting = dcr_semantics.is_accepting(sp_dcr_instance[name])
                    if accepting & executed:
                        # if the event did execute and is accepting then reset the subprocess to its initial marking
                        sp_dcr_instance[name] = deepcopy(sp_dcr_dict[name])
                        # also replace the event with the subprocess in the new event log
                        event['concept:name'] = name
                        sp_event = event
            if not sp_event:
                sp_event = event
            sp_trace.append(sp_event)
        subprocess_log.append(sp_trace)
    # now run the dcr graph with the subprocess events replaced as the subprocess
    subprocess_dcr = alg.apply(subprocess_log, alg.DCR_BASIC, findAdditionalConditions=findAdditionalConditions)
    for sp_name, internal_events in subprocesses.items():
        external_events = basic_dcr['events'].difference(internal_events)
        # external (outside sp) to internal (subprocess)
        for external_event in external_events:
            for rel in ['conditionsFor', 'responseTo', 'includesTo', 'excludesTo']:
                # Given rel
                # external events to internal events
                # external events to internal events AND subprocesses
                if external_event in basic_dcr[rel] and external_event in subprocess_dcr[rel]:
                    e2i = basic_dcr[rel][external_event].intersection(internal_events)
                    e2_sp = subprocess_dcr[rel][external_event].intersection(set([sp_name]))
                    if len(e2_sp) == 0:
                        if external_event not in subprocess_dcr[rel]:
                            subprocess_dcr[rel][external_event] = set()
                        subprocess_dcr[rel][external_event] = subprocess_dcr[rel][external_event].union(e2i)
        # internal (subprocess) to external (outside sp)
        for internal_event in internal_events:
            for rel in ['conditionsFor', 'responseTo', 'includesTo', 'excludesTo']:
                if internal_event in basic_dcr[rel] and sp_name in subprocess_dcr[rel]:
                    i2e = basic_dcr[rel][internal_event].intersection(external_events)
                    sp2e = subprocess_dcr[rel][sp_name].intersection(external_events)
                    i2e_not_sp2e = i2e.difference(sp2e)
                    if internal_event not in subprocess_dcr[rel]:
                        subprocess_dcr[rel][internal_event] = set()
                    subprocess_dcr[rel][internal_event] = subprocess_dcr[rel][internal_event].union(i2e_not_sp2e)
    subprocess_dcr['events'] = subprocess_dcr['events'].union(basic_dcr['events'])
    subprocess_dcr['marking']['included'] = subprocess_dcr['marking']['included'].union(
        basic_dcr['marking']['included'])
    subprocess_dcr['subprocesses'] = {}
    for name, sp_dcr in sp_dcr_dict.items():
        subprocess_dcr['subprocesses'][name] = sp_dcr
        # TODO: add internal to external relations add external to internal relations
        # filter whatever is already applied on the subprocess.
    return subprocess_dcr, subprocess_log


def apply(log, findAdditionalConditions=True, discardSelfInPredecessors=True, **kwargs):
    event_log = log
    disc_sp_t = DiscoverSubprocess()
    disc_sp_t.createLogAbstraction(event_log)
    log_abstraction = deepcopy(disc_sp_t.logAbstraction)
    events = log_abstraction['events']
    if discardSelfInPredecessors:
        for e in events:
            if e in log_abstraction['predecessor'] and e in log_abstraction['predecessor'][e]:
                log_abstraction['predecessor'][e].discard(e)
            if e in log_abstraction['successor'] and e in log_abstraction['successor'][e]:
                log_abstraction['successor'][e].discard(e)

    cluster_dict = {}
    keys = sorted(log_abstraction['predecessor'].keys())
    for k in keys:
        preds_set = frozenset(sorted(log_abstraction["predecessor"][k]))
        if preds_set in cluster_dict.keys():
            cluster_dict[preds_set].add(k)
        else:
            cluster_dict[preds_set] = set([k])

    subprocesses = {}
    subprocess_notation = 'S'
    i = 0
    for k, v in cluster_dict.items():
        if len(v) > 1:
            subprocesses[f'{subprocess_notation}{i}'] = frozenset(v)
            i = i + 1
    # now mine the dcr graph inside the subprocess
    sp_dcr_dict = {}
    for name, subprocess in subprocesses.items():
        sp_dcr_dict[name] = {'events': subprocess,
                             'conditionsFor': {},
                             'milestonesFor': {},
                             'responseTo': {},
                             'includesTo': {},
                             'excludesTo': {},
                             'marking': {'included': subprocess,
                                         'pending': set(),
                                         'executed': set()}
                             }
        # subset_log = subprocess_event_log[subprocess_event_log['concept:name'].isin(subprocess)]
        # subprocess_dcr[name] = alg.apply(subset_log, alg.DCR_BASIC, findAdditionalConditions=findAdditionalConditions)

    # now replay inside the dcr graph and replace with a subprocess
    subprocess_log = pm4py.objects.log.obj.EventLog()
    trace: pm4py.objects.log.obj.Trace
    event: pm4py.objects.log.obj.Event
    for trace in event_log:
        # only replace with the subprocess when the subprocess is accepting
        sp_trace = pm4py.objects.log.obj.Trace()
        for event in trace:
            # set all subprocess dcr graphs to their initial state
            sp_dcr_instance = deepcopy(sp_dcr_dict)
            sp_event = None
            for name, sp in subprocesses.items():
                if event['concept:name'] in sp:
                    # if the event is in the subprocess then execute it within the subprocess model
                    executed = dcr_semantics.execute(event['concept:name'],
                                                     sp_dcr_instance[name])  # TODO: check if it always executes
                    accepting = dcr_semantics.is_accepting(sp_dcr_instance[name])
                    if accepting & executed:
                        # if the event did execute and is accepting then reset the subprocess to its initial marking
                        sp_dcr_instance[name] = deepcopy(sp_dcr_dict[name])
                        # also replace the event with the subprocess in the new event log
                        event['concept:name'] = name
                        sp_event = event
            if not sp_event:
                sp_event = event
            sp_trace.append(sp_event)
        subprocess_log.append(sp_trace)
    # now run the dcr graph with the subprocess events replaced as the subprocess
    subprocess_dcr = alg.apply(subprocess_log, alg.DCR_BASIC, findAdditionalConditions=findAdditionalConditions)
    basic_dcr = alg.apply(event_log, alg.DCR_BASIC, findAdditionalConditions=findAdditionalConditions)
    for sp_name, internal_events in subprocesses.items():
        external_events = basic_dcr['events'].difference(internal_events)
        # external (outside sp) to internal (subprocess)
        for external_event in external_events:
            for rel in ['conditionsFor', 'responseTo', 'includesTo', 'excludesTo']:
                # Given rel
                # external events to internal events
                # external events to internal events AND subprocesses
                if external_event in basic_dcr[rel] and external_event in subprocess_dcr[rel]:
                    e2i = basic_dcr[rel][external_event].intersection(internal_events)
                    e2_sp = subprocess_dcr[rel][external_event].intersection(set([sp_name]))
                    if len(e2_sp) == 0:
                        if external_event not in subprocess_dcr[rel]:
                            subprocess_dcr[rel][external_event] = set()
                        subprocess_dcr[rel][external_event].union(e2i)
        # internal (subprocess) to external (outside sp)
        for internal_event in internal_events:
            for rel in ['conditionsFor', 'responseTo', 'includesTo', 'excludesTo']:
                if internal_event in basic_dcr[rel] and sp_name in subprocess_dcr[rel]:
                    i2e = basic_dcr[rel][internal_event].intersection(external_events)
                    sp2e = subprocess_dcr[rel][sp_name].intersection(external_events)
                    i2e_not_sp2e = i2e.difference(sp2e)
                    if internal_event not in subprocess_dcr[rel]:
                        subprocess_dcr[rel][internal_event] = set()
                    subprocess_dcr[rel][internal_event].union(i2e_not_sp2e)

    subprocess_dcr['subprocesses'] = {}
    for name, sp_dcr in sp_dcr_dict.items():
        subprocess_dcr['subprocesses'][name] = sp_dcr
        # TODO: add internal to external relations add external to internal relations
        # filter whatever is already applied on the subprocess.

    return subprocess_dcr


class DiscoverSubprocess:

    def __init__(self):
        self.graph = {
            'events': {},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': set(),
                        'included': set(),
                        'pending': set()
                        },
        }
        self.logAbstraction = {
            'events': set(),
            'traces': [[]],
            'atMostOnce': set(),
            'chainPrecedenceFor': {},
            'precedenceFor': {},
            'predecessor': {},
            'responseTo': {},
            'successor': {}
        }

    def mine(self, log, findAdditionalConditions=True):
        '''
        Parameters
        ----------
        log : the event log loaded using read_xes from pm4py
        findAdditionalConditions : apply the last step of the algorithm? True (default) or False

        Returns
        -------
        A mined dcr graph with the 4 basic relations: condition, response, include and exclude
        '''
        self.createLogAbstraction(log)
        self.mineFromAbstraction(findAdditionalConditions=findAdditionalConditions)
        # if graph_path:
        #     self.writeGraph(graph_path)
        return self.graph

    def createLogAbstraction(self, log):
        '''
        Main mining
        :param log: pm4py event log
        :param graph_path: where to save the log
        :return: 0 for success anything else for failure
        '''
        activities = get_event_attribute_values(log, "concept:name")
        events = set(activities)
        self.logAbstraction['events'] = events.copy()
        self.logAbstraction['traces'] = log
        self.logAbstraction['atMostOnce'] = events.copy()
        for event in events:
            self.logAbstraction['chainPrecedenceFor'][event] = events.copy() - set([event])
            self.logAbstraction['precedenceFor'][event] = events.copy() - set([event])
            self.logAbstraction['predecessor'][event] = set()
            self.logAbstraction['responseTo'][event] = events.copy() - set([event])
            self.logAbstraction['successor'][event] = set()

        for trace in self.logAbstraction['traces']:
            self.parseTrace(trace)

        for i in self.logAbstraction['predecessor']:
            for j in self.logAbstraction['predecessor'][i]:
                self.logAbstraction['successor'][j].add(i)

        return 0

    def parseTrace(self, trace):
        '''
        :param trace: array each trace one row and then events in order
        :return: 0 if success anything else for failure
        '''
        localAtLeastOnce = set()
        localSeenOnlyBefore = {}
        lastEvent = ''
        for event_dict in trace:
            event = event_dict['concept:name']
            # All events seen before this one must be predecessors
            self.logAbstraction['predecessor'][event] = self.logAbstraction['predecessor'][event].union(
                localAtLeastOnce)
            # If event seen before in trace, remove from atMostOnce
            if event in localAtLeastOnce:
                self.logAbstraction['atMostOnce'].discard(event)
            localAtLeastOnce.add(event)
            # Precedence for (event): All events that occured
            # before (event) are kept in the precedenceFor set
            self.logAbstraction['precedenceFor'][event] = self.logAbstraction['precedenceFor'][event].intersection(
                localAtLeastOnce)
            # Chain-Precedence for (event): Some event must occur
            # immediately before (event) in all traces
            if lastEvent != '':  # TODO: objects vs strings in sets
                # If first time this clause is encountered - leaves lastEvent in chain-precedence set.
                # The intersect is empty if this clause is encountered again with another lastEvent.
                self.logAbstraction['chainPrecedenceFor'][event] = self.logAbstraction['chainPrecedenceFor'][
                    event].intersection(set([lastEvent]))
            else:
                # First event in a trace, and chainPrecedence is therefore not possible
                self.logAbstraction['chainPrecedenceFor'][event] = set()
            # To later compute responses we note which events were seen before (event) and not after
            if len(self.logAbstraction['responseTo'][event]) > 0:
                # Save all events seen before (event)
                localSeenOnlyBefore[event] = localAtLeastOnce.copy()

            # Clear (event) from all localSeenOnlyBefore, since (event) has now occurred after
            for key in localSeenOnlyBefore:
                localSeenOnlyBefore[key].discard(event)
            lastEvent = event

        for event in localSeenOnlyBefore:
            # Compute set of events in trace that happened after (event)
            seenOnlyAfter = localAtLeastOnce.difference(localSeenOnlyBefore[event])
            # Delete self-relation
            seenOnlyAfter.discard(event)
            # Set of events that always happens after (event)
            self.logAbstraction['responseTo'][event] = self.logAbstraction['responseTo'][event].intersection(
                seenOnlyAfter)

        return 0

    # Removes redundant relations based on transitive closure
    def optimizeRelation(self, relation):
        '''
        if cond and resp A -> B, B -> C then you can remove an existing relation A -> C
        :param relation:
        :return:
        '''
        for eventA in relation:
            for eventB in relation[eventA]:
                relation[eventA] = relation[eventA].difference(relation[eventB])
        return relation

    def optimizeRelationTransitiveReduction(self, relation):
        # TODO: 1. Adj. List to Adj Matrix, 2. Transive reduction, 3. back to Adj. List
        for eventA in relation:
            for eventB in relation[eventA]:
                print('af')

    def mineFromAbstraction(self, findAdditionalConditions: bool = True):
        '''
        :param findAttitionalConditions:
        :return: a dcr graph
        '''
        # Initialize graph
        # Note that events become an alias, but this is irrelevant since events are never altered
        self.graph['events'] = self.logAbstraction['events'].copy()
        self.graph['marking']['included'] = self.logAbstraction['events'].copy()

        # Initialize all mappings to avoid indexing errors
        for event in self.graph['events']:
            self.graph['conditionsFor'][event] = set()
            self.graph['excludesTo'][event] = set()
            self.graph['includesTo'][event] = set()
            self.graph['responseTo'][event] = set()
            self.graph['milestonesFor'][event] = set()

        # Mine self-exclusions
        for event in self.logAbstraction['atMostOnce']:
            self.graph['excludesTo'][event].add(event)

        # Mine responses from logAbstraction
        self.graph['responseTo'] = deepcopy(self.logAbstraction['responseTo'])
        # Remove redundant responses
        self.graph['responseTo'] = self.optimizeRelation(self.graph['responseTo'])
        # Mine conditions from logAbstraction
        self.graph['conditionsFor'] = deepcopy(self.logAbstraction['precedenceFor'])
        # remove redundant conditions
        self.graph['conditionsFor'] = self.optimizeRelation(self.graph['conditionsFor'])

        # For each chainprecedence(i,j) we add: include(i,j) exclude(j,j)
        for j in self.logAbstraction['chainPrecedenceFor']:
            for i in self.logAbstraction['chainPrecedenceFor'][j]:
                self.graph['includesTo'][i].add(j)
                self.graph['excludesTo'][j].add(j)

        # Additional excludes based on predecessors / successors
        for event in self.logAbstraction['events']:
            # Union of predecessor and successors sets, i.e. all events occuring in the same trace as event
            coExisters = self.logAbstraction['predecessor'][event].union(self.logAbstraction['successor'][event])
            nonCoExisters = self.logAbstraction['events'].difference(coExisters)
            nonCoExisters.discard(event)
            # Note that if events i & j do not co-exist, they should exclude each other.
            # Here we only add i -->% j, but on the iteration for j, j -->% i will be added.
            self.graph['excludesTo'][event] = self.graph['excludesTo'][event].union(nonCoExisters)

            # if s precedes (event) but never succeeds (event) add (event) -->% s if s -->% s does not exist
            precedesButNeverSuceeds = self.logAbstraction['predecessor'][event].difference(
                self.logAbstraction['successor'][event])
            for s in precedesButNeverSuceeds:
                if not s in self.graph['excludesTo'][s]:
                    self.graph['excludesTo'][event].add(s)

        # Removing redundant excludes.
        # If r always precedes s, and r -->% t, then s -->% t is (mostly) redundant
        for s in self.logAbstraction['precedenceFor']:
            for r in self.logAbstraction['precedenceFor'][s]:
                for t in self.graph['excludesTo'][r]:
                    self.graph['excludesTo'][s].discard(t)

        if findAdditionalConditions:
            # Mining additional conditions:
            # Every event, x, that occurs before some event, y, is a possible candidate for a condition x -->* y
            # This is due to the fact, that in the traces where x does not occur before y, x might be excluded
            possibleConditions = deepcopy(self.logAbstraction['predecessor'])

            # Replay entire log, filtering out any invalid conditions
            for trace in self.logAbstraction['traces']:

                localSeenBefore = set()
                included = self.logAbstraction['events'].copy()
                for event_dict in trace:
                    event = event_dict['concept:name']
                    # Compute conditions that still allow event to be executed
                    excluded = self.logAbstraction['events'].difference(included)
                    validConditions = localSeenBefore.union(excluded)
                    # Only keep valid conditions
                    possibleConditions[event] = possibleConditions[event].intersection(validConditions)
                    # Execute excludes starting from (event)
                    included = included.difference(self.graph['excludesTo'][event])
                    # Execute includes starting from (event)
                    included = included.union(self.graph['includesTo'][event])

            # Now the only possibleCondtitions that remain are valid for all traces
            # These are therefore added to the graph
            for key in self.graph['conditionsFor']:
                self.graph['conditionsFor'][key] = self.graph['conditionsFor'][key].union(possibleConditions[key])

            # Removing redundant conditions
            self.graph['conditionsFor'] = self.optimizeRelation(self.graph['conditionsFor'])

        return 0
