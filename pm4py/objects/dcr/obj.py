from enum import Enum
#from collections import Counter
#from typing import Tuple

#import numpy as np

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
    'labelMapping': {}
}


class Marking:
    """
    Class object inspired by implementation of prototype of pm4py-dcr
    responsible for storing the state of the DCR graph
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

    # built-in functions for printing a visual string representation
    def __str__(self) -> str:
        return f'( {self.__executed},{self.__included},{self.__pending})'
    def __iter__(self):
        yield 'executed', self.__executed
        yield 'included', self.__included
        yield 'pending', self.__pending


class DCR_Graph:
    """
    This implementation is based on the thoery of this Paper:
    Author: Thomas T. Hildebrandt and Raghava Rao Mukkamala,
    Title: Declarative Event-BasedWorkflow as Distributed Dynamic Condition Response Graphs
    publisher: Electronic Proceedings in Theoretical Computer Science. EPTCS, Open Publishing Association, 2010, pp. 59–73. doi: 10.4204/EPTCS.69.5.
    """

    # initiate the objects: contains events ID, activity, the 4 relations, markings, roles and principals

    def __init__(self, template):
        # events and logs are essentially the same, and events was used as an identification for activities
        # in essence, activities were directly mined, but it was based on the event idenfication.
        self.__events = set(template['events'])
        self.__conditionsFor = template['conditionsFor']
        self.__responseTo = template['responseTo']
        self.__includesTo = template['includesTo']
        self.__excludesTo = template['excludesTo']
        self.__marking = Marking(template['marking']['executed'], template['marking']['included'],
                                 template['marking']['pending'])

    # def __lt__(self, other):
    #     return len(self.events) < len(other.events)

    # @property functions to extraxt values used for data manipulation and testing
    @property
    def events(self):
        return self.__events

    @property
    def labels(self):
        return self.__labels

    @property
    def labelMapping(self):
        return self.__labelMapping

    @property
    def conditionsFor(self):
        return self.__conditionsFor

    @property
    def responseTo(self):
        return self.__responseTo

    @property
    def includesTo(self):
        return self.__includesTo

    @property
    def excludesTo(self):
        return self.__excludesTo

    @property
    def marking(self):
        return self.__marking


    # in_built functions to print
    def __iter__(self):
        yield 'events', self.__events
        yield 'conditionsFor', self.__conditionsFor
        yield 'milestonesFor', {}
        yield 'responseTo', self.__responseTo
        yield 'includesTo', self.__includesTo
        yield 'excludesTo', self.excludesTo
        yield 'marking', dict(self.__marking)
        yield 'conditionsForDelays', {}
        yield 'responseToDeadlines', {}
        yield 'subprocesses', {}
        yield 'nestings', {}
        yield 'labels', set()
        yield 'labelMapping', {}

    def __repr__(self):
        return str('{' +
                   'events: '+str(self.events) + ', ' +
                   'conditionsFor: '+str(self.conditionsFor) + ', ' +
                   'responseTo: '+str(self.responseTo) + ', ' +
                   'includesTo'+str(self.includesTo) + ', ' +
                   'excludesTo'+str(self.excludesTo) + ', ' +
                   'marking'+str(self.marking)
                   + '}')

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.conditionsFor == other.conditionsFor and self.responseTo == other.responseTo and self.includesTo == other.includesTo and self.excludesTo == other.excludesTo

    def __hash__(self) -> int:
        return hash(self.__name)

    def __getitem__(self, item):
        classname = self.__class__.__name__
        # set containing names of superclass if exist
        superClassName = set()
        if self.__class__.__bases__ != {'object'}:
            for base in self.__class__.__bases__:
                superClassName.add(base.__name__)
        temp_dict = {}
        for i in self.__dict__.keys():
            if classname not in i:
                for j in superClassName:
                    newname = i.removeprefix("_" + j + "__")
                    temp_dict[newname] = self.__dict__[i]
            else:
                newname = i.removeprefix("_" + classname + "__")
                temp_dict[newname] = self.__dict__[i]
        if item in temp_dict:
            return temp_dict[item]
        else:
            return {}

    def __repr__(self):
        return str('{' +
                   'events: '+str(self.events) + ', ' +
                   'conditionsFor: '+str(self.conditionsFor) + ', ' +
                   'responseTo: '+str(self.responseTo) + ', ' +
                   'includesTo'+str(self.includesTo) + ', ' +
                   'excludesTo'+str(self.excludesTo) + ', ' +
                   'marking'+str(self.marking)
                   + '}')
