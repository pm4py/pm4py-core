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
        events
            the events in the DCR Graphs

        """
        self.__executed = initial_marking.executed
        self.__included = initial_marking.included
        self.__pending = initial_marking.pending

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


class DCR_Graph(object):
    """
    The DCR Structure was implemented according to definition 3 in [1].

    References
    ----------
    .. [1] Thomas T. Hildebrandt and Raghava Rao Mukkamala, "Declarative Event-BasedWorkflow as Distributed Dynamic Condition Response Graphs",
      Electronic Proceedings in Theoretical Computer Science — 2011, Volume 69, 59–73. `DOI <10.4204/EPTCS.69.5>`_.
    """

    # initiate the objects: contains events ID, activity, the 4 relations, markings, roles and principals
    def __init__(self, template=None):
        # DisCoveR uses bijective labelling, each event has one label
        self.__events = set() if None else template['events']
        self.__marking = Marking(set(), set(), set()) if None else (
            Marking(template['marking']['executed'],template['marking']['included'], template['marking']['pending']))
        self.__labels = set() if None else template['labels']
        self.__conditionsFor = {} if None else template['conditionsFor']
        self.__responseTo = {} if None else template['responseTo']
        self.__includesTo = {} if None else template['includesTo']
        self.__excludesTo = {} if None else template['excludesTo']
        self.__labelMapping = {} if None else template['labelMapping']

    # @property functions to extract values used for data manipulation and testing
    @property
    def events(self) -> Set[str]:
        return self.__events

    @property
    def marking(self) -> Marking:
        return self.__marking

    @property
    def labels(self) -> Set[str]:
        return self.__labels

    @property
    def conditionsFor(self) -> Dict[str, Set[str]]:
        return self.__conditionsFor

    @property
    def responseTo(self) -> Dict[str, Set[str]]:
        return self.__responseTo

    @property
    def includesTo(self) -> Dict[str, Set[str]]:
        return self.__includesTo

    @property
    def excludesTo(self) -> Dict[str, Set[str]]:
        return self.__excludesTo

    @property
    def labelMapping(self) -> Dict[str, Set[str]]:
        return self.__labelMapping

    def getEvent(self, activity: str) -> str:
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
        event
            event ID

        Returns
        -------
        activity
            the activity of the event
        """
        activity = self.__labelMapping[event].pop()
        self.__labelMapping[event].add(activity)
        return activity

    def getConstraints(self) -> int:
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
        return self.conditionsFor == other.conditionsFor and self.responseTo == other.responseTo and self.includesTo == other.includesTo and self.excludesTo == other.excludesTo

    def __getitem__(self, item):
        for key, value in vars(self).items():
            if item == key.split("_")[-1]:
                return value

    def __setitem__(self, item, value):
        for key,_ in vars(self).items():
            if item == key.split("_")[-1]:
                setattr(self,key,value)

