from copy import deepcopy

import numpy as np
import pandas as pd

import pm4py.utils
from pm4py import get_event_attribute_values
from pm4py.objects.dcr.obj import dcr_template
from enum import Enum
from typing import Tuple, Dict, Set, Any, List, Union
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.log.obj import EventLog
from pm4py.objects.dcr.obj import DcrGraph


# these parameters are used in case of attribute has a custom name, in which case it can be specified on call
class Parameters(Enum):
    """
    An enumeration class to hold parameter keys used for specifying the activity and case identifier keys
    within a log during the DCR discovery process.

    Attributes
    ----------
    ACTIVITY_KEY : str
        The key used to identify the activity attribute in the event log.
    CASE_ID_KEY : str
        The key used to identify the case identifier attribute in the event log.
    """
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def apply(log, findAdditionalConditions=True, parameters = None) -> Tuple[DcrGraph,Dict[str, Any]]:
    """
    Discovers a DCR graph model from an event log, using algorithm described in [1]_.

    Parameters
    ----------
    log
        event log (pandas dataframe)
    findAdditionalConditions
        bool value to identify if additional conditions should be mined
    parameters
        Possible parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY
        - Parameters.Case_ID_KEY
    Returns
    -------
    tuple(dict,dict)
        returns tuple of dictionaries containing the dcr_graph and the abstracted log used to mine the graph

    References
    ----------
    .. [1]
        C. O. Back et al., "DisCoveR: accurate and efficient discovery of declarative process models",
        International Journal on Software Tools for Technology Transfer, 2022, 24:563–587. 'DOI' <https://doi.org/10.1007/s10009-021-00616-0>_.

    """
    disc = Discover()
    return disc.mine(log, findAdditionalConditions, parameters = parameters)


class Discover:
    """
    The Discover class is responsible for mining DCR graphs from event logs.

    Attributes
    ----------
    graph : dict
        A dictionary representing the DCR graph, initialized from a template.
    logAbstraction : dict
        A dictionary containing abstracted information from the event log to be mined.

    Methods
    ----------
    mine(log: Union[EventLog, pd.DataFrame], findAdditionalConditions: bool = True, parameters: Optional[dict] = None) -> Tuple[DCR_Graph, Dict[str, Any]]:
        Mines a DCR graph and the log abstraction from an event log.

    createLogAbstraction(log: Union[EventLog, pd.DataFrame], activity_key: str, case_key: str) -> int:
        Creates an abstraction of the event log to facilitate the mining process.

    parseTrace(trace: List[str]) -> int:
        Parses a single trace to extract relations between events.

    optimizeRelation(relation: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
        Optimizes a relation by removing redundant relations based on transitive closure.

    mineFromAbstraction(findAdditionalConditions: bool = True) -> int:
        Mines DCR constraints from the log abstraction.
    """
    def __init__(self):
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

    def mine(self, log: Union[EventLog,pd.DataFrame], findAdditionalConditions=True, parameters=None) -> Tuple[DcrGraph,Dict[str, Any]]:
        """
        Method used for calling the underlying mining algorithm used for discovery of DCR Graphs

        Parameters
        ----------
        log
            an event log as EventLog or pandas.DataFrame
        findAdditionalConditions
            Condition for mining additional condition: True (default) or False

        parameters
                activity_key: optional parameter, used to identify the activities in the log
                case_id_key: optional parameter, used to identify the cases executed in the log

        Returns
        -------
        Tuple[DcrGraph,Dict[str, Any]]
            returns a tuple containing:
            - The DCR Graph
            - The log abstraction used for mining
        """
        activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
        case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
        self.createLogAbstraction(log, activity_key, case_id_key)
        self.mineFromAbstraction(findAdditionalConditions=findAdditionalConditions)
        return DcrGraph(self.graph), self.logAbstraction

    def createLogAbstraction(self, log: [EventLog,pd.DataFrame], activity_key: str, case_key: str) -> int:
        """
        Performs the mining of abstraction log, will map event log onto a selection of DECLARE templates.

        Parameters
        ----------
        log : EventLog | pd.DataFrame
            The event log to be abstracted.
        activity_key : str
            The attribute key used to identify the activities recorded in the log.
        case_key : str
            The attribute key used to identify the cases recorded in the log.

        Returns
        -------
        int
            Returns 0 for success, and any other value for failure.
        """
        # initiate the activities, in DisCoveR, activities and event id is mapped bijectively
        activities = get_event_attribute_values(log, activity_key)
        events = set(activities)

        # load events in to log abstraction
        self.logAbstraction['events'] = events.copy()
        log = pm4py.project_on_event_attribute(log, case_id_key=case_key)

        # flatten the event log, all traces are equally significant
        traces = set(tuple(i) for i in log)
        traces = [list(i) for i in traces]

        self.logAbstraction['traces'] = traces
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

    def parseTrace(self, trace: List[str]) -> int:
        """
        Parses a trace to mine DEClARE constraints.

        Parameters
        ----------
        trace : List[str]
            A list representing a trace, where each element is an event, and the order of events is maintained.

        Returns
        -------
        int
            Returns 0 on success, and any other value on failure.

        Notes
        -----
        This method performs the following key steps:
        - Identifies and updates predecessor relationships for each event in the trace.
        - Updates 'atMostOnce', 'precedenceFor', and 'chainPrecedenceFor' sets in the log abstraction based on the trace events.
        - Computes and updates 'responseTo' sets in the log abstraction based on the events seen before and after each event in the trace.
        """
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

    def optimizeRelation(self, relation: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
        """
        Optimizes a given relation by removing redundant connections based on transitive closure.

        For instance, if there are relations A -> B, B -> C, then an existing relation A -> C can be removed
        as it is implied by the transitive nature of the other relations.

        Parameters
        ----------
        relation : Dict[str, Set[str]]
            A dictionary representing a relation, where keys are starting points and values are sets of endpoints.

        Returns
        -------
        Dict[str, Set[str]]
            An optimized version of the input relations, with redundant connections removed.
        """
        # Sorted dict to avoid possibly non-deterministic behavior due to unordered nature of dict
        relation = dict(sorted(relation.items(), key=lambda conditions: len(conditions[1]),reverse=True))
        for eventA in relation:
            for eventB in relation[eventA]:
                relation[eventA] = relation[eventA].difference(relation[eventB])
        return relation

    def mineFromAbstraction(self, findAdditionalConditions: bool = True) -> int:
        """
        Mines DCR constraints based on the DECLARE templates stored in the log abstraction.

        This method initializes a graph and mines conditions, responses, self-exclusions, and additional conditions
        (if specified) from the user. It also optimizes the relations by removing redundant relations based
        on transitive closure.

        Parameters
        ----------
        findAdditionalConditions : bool, optional
            Specifies whether to mine additional conditions. Default is True.

        Returns
        -------
        int
            Returns 0 if successful, anything else for failure.
        """
        # Initialize graph
        # Note that events become an alias, but this is irrelevant since events are never altered
        self.graph['events'] = self.logAbstraction['events'].copy()

        #insert labels and label mapping, used for bijective label mapping
        self.graph['labels'] = deepcopy(self.graph['events'])

        # All events are initially included
        self.graph['marking']['included'] = self.logAbstraction['events'].copy()

        # Initialize all to_petri_net to avoid indexing errors
        for event in self.graph['events']:
            self.graph['labelMapping'][event] = {event}
            self.graph['conditionsFor'][event] = set()
            self.graph['excludesTo'][event] = set()
            self.graph['includesTo'][event] = set()
            self.graph['responseTo'][event] = set()


        # Mine conditions from logAbstraction
        self.graph['conditionsFor'] = deepcopy(self.logAbstraction['precedenceFor'])
        # remove redundant conditions
        self.graph['conditionsFor'] = self.optimizeRelation(self.graph['conditionsFor'])
        # Mine responses from logAbstraction
        self.graph['responseTo'] = deepcopy(self.logAbstraction['responseTo'])
        # Remove redundant responses
        self.graph['responseTo'] = self.optimizeRelation(self.graph['responseTo'])

        # Mine self-exclusions
        for event in self.logAbstraction['responseTo']:
            if event in self.logAbstraction['atMostOnce']:
                self.graph['excludesTo'][event].add(event)

        # For each chainprecedence(i,j) we add: include(i,j) exclude(j,j)
        for j in self.logAbstraction['chainPrecedenceFor']:
            for i in self.logAbstraction['chainPrecedenceFor'][j]:
                self.graph['excludesTo'][j].add(j)
                self.graph['includesTo'][i].add(j)

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
            """
            Mining additional conditions:
            Every event, x, that occurs before some event, y, is a possible candidate for a condition x -->* y
            This is due to the fact, that in the traces where x does not occur before y, x might be excluded
            """
            possibleConditions = deepcopy(self.logAbstraction['predecessor'])
            # Replay entire log, filtering out any invalid conditions
            for trace in self.logAbstraction['traces']:
                localSeenBefore = set()
                included = self.logAbstraction['events'].copy()
                for event in trace:
                    # Compute conditions that still allow event to be executed
                    excluded = self.logAbstraction['events'].difference(included)
                    validConditions = localSeenBefore.union(excluded)
                    # Only keep valid conditions
                    possibleConditions[event] = possibleConditions[event].intersection(validConditions)
                    # Execute excludes starting from (event)
                    included = included.difference(self.graph['excludesTo'][event])
                    # Execute includes starting from (event)
                    included = included.union(self.graph['includesTo'][event])
                    localSeenBefore.add(event)

            # Now the only possible Condtitions that remain are valid for all traces
            # These are therefore added to the graph
            for key in self.graph['conditionsFor']:
                self.graph['conditionsFor'][key] = self.graph['conditionsFor'][key].union(possibleConditions[key])

            # Removing redundant conditions
            self.graph['conditionsFor'] = self.optimizeRelation(self.graph['conditionsFor'])
        self.clean_empty_sets()
        return 0

    def clean_empty_sets(self):
        for k, v in deepcopy(self.graph).items():
            if k in ['conditionsFor', 'responseTo', 'excludesTo', 'includesTo']:
                v_new = {}
                for k2, v2 in v.items():
                    if v2:
                        v_new[k2] = set([v3 for v3 in v2 if v3 is not set()])
                self.graph[k] = v_new