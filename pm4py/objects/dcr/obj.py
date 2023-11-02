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
    # <<<<<<< HEAD
    'labelMapping': {},
    'roles': set(),
    'principals': set(),
    'roleAssignments': {},
    'readRoleAssignments': {}
    # >>>>>>> 40a38596ee1706d65f38e531c20db84f2ffdedba
}


class Marking:
    """
    This class contains the set of all markings M(G), in which it contains three sets:
    M(G) = P(E) x P(E) x P(E)
    where P(E) represent the set of included, executed and pending events.
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

    def reset(self, events) -> None:
        self.__executed = set()
        self.__included = events
        self.__pending = set()

    # built-in functions for printing a visual string representation
    def __str__(self) -> str:
        return f'{{executed: {self.__executed}, included: {self.__included}, pending: {self.__pending}}}'

    def __getitem__(self, item):
        for key, value in vars(self).items():
            if item == key.split("_")[-1]:
                return value


class DCR_Graph(object):
    """
    The DCR Structure was implemented according to definition 3 in [1].

    The structure of the graphs is:
    G = (E,M,Act,->*,*->,->(+,%),l)

    References
    ----------
    .. [1] Thomas T. Hildebrandt and Raghava Rao Mukkamala, "Declarative Event-BasedWorkflow as Distributed Dynamic Condition Response Graphs",
      Electronic Proceedings in Theoretical Computer Science — 2011, Volume 69, 59–73. `DOI <10.4204/EPTCS.69.5>`_.
    """

    # initiate the objects: contains events ID, activity, the 4 relations, markings, roles and principals
    def __init__(self, template):
        # DisCoveR uses bijective labelling, each event has one label
        self.__events = set(template['events'])
        self.__marking = Marking(template['marking']['executed'], template['marking']['included'],
                                 template['marking']['pending'])
        self.__labels = template['labels']
        self.__conditionsFor = template['conditionsFor']
        self.__responseTo = template['responseTo']
        self.__includesTo = template['includesTo']
        self.__excludesTo = template['excludesTo']
        self.__labelMapping = template['labelMapping']

    # @property functions to extract values used for data manipulation and testing
    @property
    def events(self) -> Set[str]:
        """
        events(set): A set representing the events in the DCR Graph
        """
        return self.__events

    @property
    def marking(self) -> Marking:
        """
        marking(:class: 'Marking'): an instance of the Marking for the DCR graph: M(G) = In(E) x Ex(E) x Pe(E)
        """
        return self.__marking

    @property
    def labels(self) -> Set[str]:
        """
        labels(set): A set representing the Activities in the DCR Graph
        """
        return self.__labels

    @property
    def conditionsFor(self) -> Dict[str, Set[str]]:
        """
        conditionsFor(dict): A dictonary representing the condition relations between events
        """
        return self.__conditionsFor

    @property
    def responseTo(self) -> Dict[str, Set[str]]:
        """
        responseTo(dict): A dictonary representing the response relations between events
        """
        return self.__responseTo

    @property
    def includesTo(self) -> Dict[str, Set[str]]:
        """
        includesTo(dict): A dictonary representing the include relations between events
        """
        return self.__includesTo

    @property
    def excludesTo(self) -> Dict[str, Set[str]]:
        """
        excludesTo(dict): A dictonary representing the exclude relations between events
        """
        return self.__excludesTo

    @property
    def labelMapping(self) -> Dict[str, Set[str]]:
        """
        labelMapping(dict): A dictionary representing the labelMapping from events to mapping is bijective
        """
        return self.__labelMapping

    def getEvent(self, activity: str) -> str:
        """
        Get the event ID of an activity from graph.

        Parameters
        ----------
        :param activity: A str representing the activity of an event

        Returns
        -------
        :return: the Event ID of a given activity
        """
        for event in self.__labelMapping:
            act = self.__labelMapping[event].pop()
            self.__labelMapping[event].add(act)
            if activity == act:
                return event

    def getActivity(self, event: str) -> str:
        """
        get the activity of an Event

        Parameters
        ----------
        :param event: event ID as string

        Returns
        -------
        :return: the activity of an event
        """
        activity = self.__labelMapping[event].pop()
        self.__labelMapping[event].add(activity)
        return activity

    def getConstraints(self) -> int:
        """
        Computes the amount of constraint that exist between events

        Returns
        -------
        :return: number of constraints
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

    def reset(self) -> None:
        """
        resets the dcr graph
        """
        self.__marking.reset(self.events.copy())

    def __repr__(self):
        return str('{' +
                   'events: ' + str(self.events) + ', ' +
                   'conditionsFor: ' + str(self.conditionsFor) + ', ' +
                   'responseTo: ' + str(self.responseTo) + ', ' +
                   'includesTo' + str(self.includesTo) + ', ' +
                   'excludesTo' + str(self.excludesTo) + ', ' +
                   'marking' + str(self.marking)
                   + '}')

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.conditionsFor == other.conditionsFor and self.responseTo == other.responseTo and self.includesTo == other.includesTo and self.excludesTo == other.excludesTo

    def __getitem__(self, item):
        for key, value in vars(self).items():
            if item == key.split("_")[-1]:
                return value