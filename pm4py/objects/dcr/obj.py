"""
This module defines the core components for modelling Declarative Process Models as
Dynamic Condition Response (DCR) Graphs.

The module encapsulates the essential elements of DCR Graphs, such as events,
relations, markings, and constraints, providing a foundational framework for
working with DCR Graphs within PM4Py.

Classes:
    Relations: An enumeration of possible relations between events in a DCR Graph.
    Marking: Represents the state of events in terms of executed, included, and pending.
    DCR_Graph: Encapsulates the structure and behavior of a DCR Graph, offering methods to query and manipulate it.

The `dcr_template` dictionary provides a blueprint for initializing new DCR Graphs with default settings.
"""

from enum import Enum
from typing import Set, Dict

class Relations(Enum):
    I = 'includesTo'
    E = 'excludesTo'
    R = 'responseTo'
    N = 'noResponseTo'
    C = 'conditionsFor'
    M = 'milestonesFor'


dcr_template = {
    'events': set(),
    'conditionsFor': {},
    'milestonesFor': {},
    'responseTo': {},
    'noResponseTo': {},
    'includesTo': {},
    'excludesTo': {},
    'marking': {'executed': set(),
                'included': set(),
                'pending': set(),
                'executedTime': {},  # Gives the time since a event was executed
                'pendingDeadline': {}  # The deadline until an event must be executed
                },
    'conditionsForDelays': {},
    'responseToDeadlines': {},
    'subprocesses': {},
    'nestings': {},
    'labels': set(),
    'labelMapping': {},
    'roles': set(),
    'principals': set(),
    'roleAssignments': {},
    'readRoleAssignments': {}
}

class Marking:
    """
    This class contains the set of all markings M(G), in which it contains three sets:
    M(G) = executed x included x pending

    Attributes
    ----------
    self.__executed: Set[str]
        The set of executed events
    self.__included: Set[str]
        The set of included events
    self.__pending: Set[str]
        the set of pending events

    Methods
    --------
    reset(self, initial_marking) -> None:
        Given the initial marking of the DCR Graph, reset the marking, to restart execution of traces


    """
    def __init__(self, executed, included, pending) -> None:
        self.__executed = executed
        self.__included = included
        self.__pending = pending

    # getters and setters for datamanipulation, mainly used for DCR semantics
    @property
    def executed(self):
        return self.__executed

    @property
    def included(self):
        return self.__included

    @property
    def pending(self):
        return self.__pending

    def reset(self, initial_marking) -> None:
        """
        Resets the marking of a DCR graph, uses the graphs event to reset included marking

        Parameters
        ----------
        initial_marking
            the events in the DCR Graphs

        """
        self.__executed = set(initial_marking['executed'])
        self.__included = set(initial_marking['included'])
        self.__pending = set(initial_marking['pending'])

    # built-in functions for printing a visual string representation
    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self):
        return f'{{executed: {self.__executed}, included: {self.__included}, pending: {self.__pending}}}'


    def __getitem__(self, item):
        for key, value in vars(self).items():
            if item == key.split("_")[-1]:
                return value

    def __setitem__(self, item, value):
        for key, _ in vars(self).items():
            if item == key.split("_")[-1]:
                setattr(self, key, value)

    def __lt__(self, other):
        return str(self) < str(other)


class DcrGraph(object):
    """
    The DCR Structure was implemented according to definition 3 in [1]_.
    Follows the idea of DCR graph as a set of tuples
    G = (E,Act,M,->*,*->,->{+,-},l)
    G graphs consist of a tuple of the events the activities,
    the marking of executed, included and pending events, all the relations, and the mapping of events to activities.

    References
    ----------
    .. [1] Thomas T. Hildebrandt and Raghava Rao Mukkamala, "Declarative Event-BasedWorkflow as Distributed Dynamic Condition Response Graphs",
      Electronic Proceedings in Theoretical Computer Science — 2011, Volume 69, 59–73. `DOI <10.4204/EPTCS.69.5>`_.

    Attributes
    ----------
    self.__events: Set[str]
        The set of all events in graph
    self.__marking: Marking
        the marking of the DCR graph loaded in
    self.__labels: Set[str]
        The set of activities in Graphs
    self.__labelMapping: Dict[str, Set[str]]:
        The set of event and their corresponding activity
    self.__condiditionsFor: Dict[str, Set[str]]:
        attribute containing all the conditions relation between events
    self.__responseTo: Dict[str, Set[str]]:
        attribute containing all the response relation between events
    self.__includesTo: Dict[str, Set[str]]:
        attribute containing all the include relations between events
    self.__excludesTo: Dict[str, Set[str]]:
        attribute containing all the exclude relations between events

    Methods
    --------
    getEvent(activity) -> str:
        returns the event of the associated activity
    getActivity(event) -> str:
        returns the activity of the given event
    getConstraints() -> int:
        returns the size of the model based on number of constraints

    Parameters
    ----------
    template : dict, optional
        A template dictionary to initialize the roles and assignments from, if provided.

    Examples
    --------
    call this module and call the following
    graph = DCR_graph(dcr_template)

    Notes
    -------
    * DCR graph can not be initialized with a partially created template, use DCR_template for easy instantiation
    """

    # initiate the objects: contains events ID, activity, the 4 relations, markings, roles and principals
    def __init__(self, template=None):
        # DisCoveR uses bijective labelling, each event has one label
        self.__events = set() if template is None else template['events']
        self.__marking = Marking(set(), set(), set()) if template is None else (
            Marking(template['marking']['executed'],template['marking']['included'], template['marking']['pending']))
        self.__labels = set() if template is None else template['labels']
        self.__conditionsFor = {} if template is None else template['conditionsFor']
        self.__responseTo = {} if template is None else template['responseTo']
        self.__includesTo = {} if template is None else template['includesTo']
        self.__excludesTo = {} if template is None else template['excludesTo']
        self.__labelMapping = {} if template is None else template['labelMapping']

    # @property functions to extract values used for data manipulation and testing
    @property
    def events(self) -> Set[str]:
        return self.__events

    @property
    def marking(self) -> Marking:
        return self.__marking

    @marking.setter
    def marking(self, value: Marking) -> None:
        self.__marking = value

    @property
    def labels(self) -> Set[str]:
        return self.__labels

    @property
    def conditions(self) -> Dict[str, Set[str]]:
        return self.__conditionsFor

    @property
    def responses(self) -> Dict[str, Set[str]]:
        return self.__responseTo

    @property
    def includes(self) -> Dict[str, Set[str]]:
        return self.__includesTo

    @property
    def excludes(self) -> Dict[str, Set[str]]:
        return self.__excludesTo

    @property
    def label_mapping(self) -> Dict[str, Set[str]]:
        return self.__labelMapping

    def get_event(self, activity: str) -> str:
        """
        Get the event ID of an activity from graph.

        Parameters
        ----------
        activity
            the activity of an event

        Returns
        -------
        event
            the event ID of activity
        """
        event = self.__labelMapping.get(activity, "None")
        if event is "None":
            return activity
        event = event.pop()
        self.__labelMapping[activity].add(event)
        return event

    def get_activity(self, event: str) -> str:
        """
        get the activity of an Event

        Parameters
        ----------
        event
            event ID

        Returns
        -------
        activity
            the activity of the event
        """
        for activity in self.__labelMapping:
            event_prime = self.__labelMapping[activity]
            event_prime = event_prime.pop()
            self.__labelMapping[activity].add(event_prime)
            if event == event_prime:
                return activity
        return event

    def get_constraints(self) -> int:
        """
        compute constraints in DCR Graph
            - conditions
            - responses
            - includes
            - excludes

        Returns
        -------
        no
            number of constraints
        """
        no = 0
        for i in self.__conditionsFor.values():
            no += len(i)
        for i in self.__responseTo.values():
            no += len(i)
        for i in self.__excludesTo.values():
            no += len(i)
        for i in self.__includesTo.values():
            no += len(i)
        return no

    def __repr__(self):
        string = ""
        for key, value in vars(self).items():
            string += str(key.split("_")[-1])+": "+str(value)+"\n"
        return string

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.conditions == other.conditions and self.responses == other.responses and self.includes == other.includes and self.excludes == other.excludes

    def __lt__(self, other):
        return str(self.obj) < str(other.obj)

    def __getitem__(self, item):
        for key, value in vars(self).items():
            if item == key.split("_")[-1]:
                return value
        return set()

    def __setitem__(self, item, value):
        for key,_ in vars(self).items():
            if item == key.split("_")[-1]:
                setattr(self, key, value)
