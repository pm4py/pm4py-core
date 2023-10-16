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
from copy import deepcopy

import numpy as np

import pm4py.utils
from pm4py import get_event_attribute_values
from pm4py.objects.dcr.obj import dcr_template
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
import time


def apply(log, findAdditionalConditions=True, parameters=None):
    """
    Discovers a DCR graph model from an event log.

    Implements DCR algorithm provided in:
    C. O. Back, T. Slaats, T. T. Hildebrandt, M. Marquard, "DisCoveR: accurate and efficient discovery of declarative process models"

    Parameters
    ----------
    log
        event log (pandas dataframe)
    findAdditionalConditions
        bool value to identify if additional conditions should be mined
    Parameters
        optional parameters, currently not used
    Returns
    -------
    tuple(dict,dict)
        returns tuple of dictionary containing the dcr_graph and the abstracted log used to mine the graph
    """
    disc = Discover()
    dcr = disc.mine(log, findAdditionalConditions, parameters=parameters)
    return dcr


class Discover:
    """
    Class constructed for the DisCoveR miner,
    initiates relevant objects used for mine and Contains all methods used for mining basic DCR graphs.
    """

    # these parameters are used in case of attribute has a custom name, in which case it can be specified on call
    def __init__(self):
        """
        initiates the dcr_template and log abstraction used for mining
        """
        self.graph = deepcopy(dcr_template)
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

    def mine(self, log, findAdditionalConditions=True, parameters=None):
        '''
        Parameters
        ----------
        log
            the event log loaded using read_xes from pm4py
        findAdditionalConditions
            apply the last step of the algorithm? True (default) or False

        case_id_key
        activity_key

        Returns
        -------
        tuple(dict,dict)
            returns a mind dcr graph and associated log abstraction used for mining
        '''
        activity_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
        case_id_key = exec_utils.get_param_value(constants.PARAMETER_CONSTANT_CASEID_KEY, parameters, constants.CASE_CONCEPT_NAME)
        self.createLogAbstraction(log, activity_key, case_id_key)
        self.mineFromAbstraction(activity_key, findAdditionalConditions=findAdditionalConditions)
        # if graph_path:
        #     self.writeGraph(graph_path)
        return self.graph, self.logAbstraction

    def createLogAbstraction(self, log, activity_key: str, case_key: str):
        '''
        Main mining
        Parameters
        ----------
        :param log: pm4py event log
        case_id_key
        activity_key

        Returns
        ----------
        :return: 0 for success anything else for failure
        '''

        """
        activities = set(get_event_attribute_values(log, activity_key)))
        events = set([str(i) for i in range(len(activities))])
        labelMapping = {}
        for i,j in zip(events,activities):
            labelMapping.update({str(i): j})
        """
        activities = get_event_attribute_values(log, activity_key)
        events = set(activities)
        self.logAbstraction['events'] = events.copy()

        start_time = time.perf_counter()
        self.logAbstraction['traces'] = pm4py.project_on_event_attribute(log, case_id_key=case_key)
        end_time = time.perf_counter()
        #print("time it took to load traces: "+str((end_time-start_time)*1000))
        self.logAbstraction['atMostOnce'] = events.copy()
        for event in events:
            self.logAbstraction['chainPrecedenceFor'][event] = events.copy() - set([event])
            self.logAbstraction['precedenceFor'][event] = events.copy() - set([event])
            self.logAbstraction['predecessor'][event] = set()
            self.logAbstraction['responseTo'][event] = events.copy() - set([event])
            self.logAbstraction['successor'][event] = set()
        start_time = time.perf_counter()
        for trace in self.logAbstraction['traces']:
            self.parseTrace(trace, activity_key)
        end_time = time.perf_counter()
        #print("time it took to mine declare templates: " + str((end_time - start_time) * 1000))
        for i in self.logAbstraction['predecessor']:
            for j in self.logAbstraction['predecessor'][i]:
                self.logAbstraction['successor'][j].add(i)
        return 0

    def parseTrace(self, trace, activity_key):
        '''
        :param trace: array each trace one row and then events in order
        :param activity_key:
        :return: 0 if success anything else for failure
        '''
        localAtLeastOnce = set()
        localSeenOnlyBefore = {}
        lastEvent = ''
        for event in trace:
            # All events seen before this one must be predecessors
            self.logAbstraction['predecessor'][event] = self.logAbstraction['predecessor'].get(event).union(
                localAtLeastOnce)
            # If event seen before in trace, remove from atMostOnce
            if event in localAtLeastOnce:
                self.logAbstraction['atMostOnce'].discard(event)
            localAtLeastOnce.add(event)
            # Precedence for (event): All events that occurred before (event) are kept in the precedenceFor set
            self.logAbstraction['precedenceFor'][event] = self.logAbstraction['precedenceFor'][event].intersection(
                localAtLeastOnce)

            # Chain-Precedence for (event): Some event must occur immediately before (event) in all traces
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

    def optimizeRelation(self, relation):
        '''
        Removes redundant relations based on transitive closure
        if cond and resp A -> B, B -> C then you can remove an existing relation A -> C
        :param relation:
        :return:
        '''
        # Sortedlist to avoid possibly non-deterministic behavior
        sortedList = list(relation.items())
        sortedList.sort(key=lambda num: len(num[1]),reverse=True)
        sortedList = [list(i) for i in sortedList]
        for i in range(len(sortedList)):
            for j in sortedList[i][1]:
                sortedList[i][1] = sortedList[i][1].difference(relation[j])
        relation = dict(sortedList)
        return relation

    def optimizeRelationTransitiveReduction(self, relation):
        # TODO: 1. Adj. List to Adj Matrix, 2. Transive reduction, 3. back to Adj. List
        for eventA in relation:
            for eventB in relation[eventA]:
                print('af')

    def mineFromAbstraction(self, activity_key, findAdditionalConditions: bool = True):
        '''
        Parameters
        ----------
        :param activity_key:
        :param findAdditionalConditions:

        Returns
        ----------
        :return: a dcr graph
        '''
        # Initialize graph
        # Note that events become an alias, but this is irrelevant since events are never altered
        self.graph['events'] = self.logAbstraction['events'].copy()
        # self.graph['labels'] = self.logAbstraction['activities'].copy()
        # self.graph['labelMapping'] = self.logAbstraction['labelMapping'].copy()
        self.graph['marking']['included'] = self.logAbstraction['events'].copy()

        # Initialize all to_petri_net to avoid indexing errors
        for event in self.graph['events']:
            self.graph['conditionsFor'][event] = set()
            self.graph['excludesTo'][event] = set()
            self.graph['includesTo'][event] = set()
            self.graph['responseTo'][event] = set()
            self.graph['milestonesFor'][event] = set()
        start_time = time.perf_counter()
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
                if j not in self.logAbstraction['atMostOnce']:
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
            precedesButNeverSucceeds = self.logAbstraction['predecessor'][event].difference(
                self.logAbstraction['successor'][event])
            for s in precedesButNeverSucceeds:
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
                for event in trace:
                    # val_list = list(self.logAbstraction['labelMapping'].values())
                    # event = str(val_list.index(event))
                    # Compute conditions that still allow event to be executed
                    excluded = self.logAbstraction['events'].difference(included)
                    validConditions = localSeenBefore.union(excluded)
                    # Only keep valid conditions
                    possibleConditions[event] = possibleConditions[event].intersection(validConditions)
                    # Execute excludes starting from (event)
                    included = included.difference(self.graph['excludesTo'][event])
                    # Execute includes starting from (event)
                    included = included.union(self.graph['includesTo'][event])

            # Now the only possible Condtitions that remain are valid for all traces
            # These are therefore added to the graph
            for key in self.graph['conditionsFor']:
                self.graph['conditionsFor'][key] = self.graph['conditionsFor'][key].union(possibleConditions[key])

            # Removing redundant conditions
            self.graph['conditionsFor'] = self.optimizeRelation(self.graph['conditionsFor'])
        end_time = time.perf_counter()
        #print("time it took to mine from LA: " + str((end_time - start_time) * 1000))

        return 0
