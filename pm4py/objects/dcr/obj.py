from enum import Enum
from collections import Counter


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
    'roleAssignments': {},
    'readRoleAssignments': {}
}


class Marking(object):
    """
    This is a per Event marking not a per graph marking
    """

    def __init__(self, executed, included, pending) -> None:
        self.__executed = executed
        self.__included = included
        self.__pending = pending
        self.__last_executed = None
        self.__deadline = None
        super().__init__()

    @property
    def executed(self):
        return self.__executed

    @executed.setter
    def executed(self, value):
        self.__executed = value

    @property
    def included(self):
        return self.__included

    @included.setter
    def included(self, value):
        self.__included = value

    @property
    def pending(self):
        return self.__pending

    @pending.setter
    def pending(self, value):
        self.__pending = value

    @property
    def last_executed(self):
        return self.__last_executed

    @last_executed.setter
    def last_executed(self, value):
        self.__last_executed = value

    @property
    def deadline(self):
        return self.__deadline

    @deadline.setter
    def deadline(self, value):
        self.__deadline = value

    def __str__(self) -> str:
        return f'( {self.__executed},{self.__included},{self.__pending})'


class Event(object):

    def __init__(self, id, label, parent, children, marking = Marking(False,True,False)) -> None:
        """

        :param id: id (assumed unique)
        :param label: label
        :param parent: parent (a graph or events)
        :param children: children (a graph or events)
        :param marking: default just included
        """
        self.__children = children
        self.__loading = False
        self.__parent = parent
        self.__id = id
        self.__label = label
        self.__events = set()
        if marking:
            self.__marking = marking
        else:
            self.__marking = Marking(False, True, False)

        self.__conditions = set()
        self.__responses = set()
        self.__milestones = set()
        self.__includes = set()
        self.__excludes = set()
        super().__init__()

    @property
    def marking(self):
        return self.__marking

    @property
    def conditions(self):
        return self.__conditions

    @property
    def responses(self):
        return self.__responses

    @property
    def milestones(self):
        return self.__milestones

    @property
    def includes(self):
        return self.__includes

    @property
    def excludes(self):
        return self.__excludes

    def isSubProcess(self):
        return len(self.__children.events) > 0

    def enabled(self):
        if isinstance(self.__parent, Event):
            if not self.__parent.enabled():
                return False

        if not self.__marking.included:
            return False

        for e in self.__events:
            if not e.is_accepting():
                return False

        for r in self.__conditions:
            if r.guard:
                e = r.src
                if e.marking.included and not e.marking.executed:
                    return False
                if r.delay:
                    if r.delay > e.marking.last_executed:
                        return False

        for r in self.__milestones:
            if r.guard:
                e = r.src
                if e.marking.included and e.marking.pending:
                    return False

        return True

    def canTimeStep(self, diff):
        if self.__marking.deadline:
            return self.__marking.deadline <= diff

    def timeStep(self, diff):
        if self.__marking.last_executed:
            self.__marking.last_executed = self.__marking.last_executed + diff
        if self.__marking.deadline:
            self.__marking.deadline = self.__marking.deadline - diff

    def execute(self):
        if self.enabled():
            self.__marking.executed = True
            self.__marking.pending = False
            self.__marking.deadline = None
            self.__marking.last_executed = 0

            for r in self.__responses:
                if r.guard:
                    e = r.trg
                    e.marking.pending = True
                    e.marking.deadline = r.deadline

            for r in self.__excludes:
                if r.guard:
                    e = r.trg
                    e.marking.included = False

            for r in self.__includes:
                if r.guard:
                    e = r.trg
                    e.marking.included = True

            if isinstance(self.__parent, Event):
                if self.__parent.enabled():
                    self.__parent.execute()

    def isAccepting(self):
        return not self.__marking.pending and self.__marking.included

    # TODO figure out what to override so that event comparisons work on names and not on labels (I assume labels are
    #  displayed and names are hidden)
    def __eq__(self, o: object) -> bool:
        if isinstance(o, Event):
            return self.__id == o.__id
        elif isinstance(o, str):
            return self.__id == o
        else:
            return super().__eq__(o)

    def __hash__(self) -> int:
        return self.__id.hash()

class DataEvent(Event):

    def __init__(self, id, label, parent, children, marking=Marking(False, True, False)) -> None:
        super().__init__(id, label, parent, children, marking)


class DCRGraph(object):

    def __init__(self, parent_graph: None) -> None:
        self.__parent_graph_temp = parent_graph
        self.__parent = None
        self.__events = set()

    def parent_graph(self):
        if self.__parent is None:
            return self.__parent_graph_temp
        else:
            return self.__parent

    def root(self):
        if self.parent_graph():
            return self.parent_graph().root()
        else:
            return self

    def remove_event(self, old: Event):
        self.__events.remove(old)
        for e in self.__events:
            e.children.remove_event(old)

    def replace_event(self, old: Event, new: Event):
        if old in self.__events:
            for r in old.conditions:
                new.conditions.add(r)
            for r in old.milestones:
                new.milestones.add(r)
            for r in old.responses:
                new.responses.add(r)
            for r in old.includes:
                new.includes.add(r)
            for r in old.excludes:
                new.excludes.add(r)
            self.__events.remove(old)
            for e in self.__events:
                self.replace_in_relation(e.conditions, old, new)
                self.replace_in_relation(e.milestones, old, new)
                self.replace_in_relation(e.responses, old, new)
                self.replace_in_relation(e.includes, old, new)
                self.replace_in_relation(e.excludes, old, new)

    def replace_in_relation(self, relation, old, new):
        for e in relation:
            if e == old:
                relation.remove(old)
                relation.add(new)

    def has_event(self, new):
        return self.get_event(new) in self.__events

    def get_event(self, new):
        '''
        Get an event based on name or if it is an Event object with the name in it
        :param new: name of the event (which is unique, unlike the label which can be whatever)
        :return:
        '''
        if new in self.__events:
            if isinstance(new, Event):
                return new
            elif isinstance(new, str):
                for e in self.__events:
                    if e == new:
                        return e
        for e in self.__events:
            if e.children.get_event(new):
                return e.children.get_event(new)
        return None

    def add_loading_event(self, new):
        if self.has_event(new):
            return self.get_event(new)
        elif self.root().has_event(new):
            return self.root().get_event(new)

        e = self.add_event(new)
        e.loading = True
        return e

    def add_event(self, id, label, marking, graph):
        '''
        :param id: id
        :param label: label
        :param marking: marking
        :param graph: DCRGraph
        :return:
        '''
        if self.has_event(id) or self.root().has_event(id):
            if self.has_event(id):
                e = self.get_event(id)
            else:
                e = self.root().get_event(id)

            if not e.loading:
                pass  # TODO make an error or exception
            else:
                self.remove_event(e)
                self.root().remove_event(e)
                e.label = label
                e.parent = self
                e.children = graph
        else:
            e = Event(id, label, self, graph)

        graph.parent = e
        e.marking.executed = marking.executed
        e.marking.included = marking.included
        e.marking.pending = marking.pending
        if marking.deadline:
            e.marking.deadline = marking.deadline
        if marking.last_executed:
            e.marking.last_executed = marking.last_executed
        self.__events.add(e)

        return e

    def check_src_and_trg_exist(self, src, trg):
        if not self.root().has_event(src):
            eSrc = self.add_loading_event(src)
        else:
            eSrc = self.root().get_event(src)

        if not self.root().has_event(trg):
            eTrg = self.add_loading_event(trg)
        else:
            eTrg = self.root().getEvent(trg)
        return eSrc, eTrg

    def add_condition(self, src, trg, delay, guard=True):
        '''
        src -->* trg
        '''
        eSrc, eTrg = self.check_src_and_trg_exist(src, trg)
        eTrg.conditions.add({'src': eSrc, 'delay': delay, 'guard': guard})

    def add_milestone(self, src, trg, guard=True):
        '''
         src --><> trg
        '''
        eSrc, eTrg = self.check_src_and_trg_exist(src, trg)
        eTrg.milestones.add({'src': eSrc, 'guard': guard})

    def add_response(self, src, trg, deadline, guard=True):
        '''
        src *--> trg
        '''
        eSrc, eTrg = self.check_src_and_trg_exist(src, trg)
        eSrc.responses.add({'trg': eTrg, 'deadline': deadline, 'guard': guard})

    def add_include(self, src, trg, guard=True):
        '''
        src -->+ trg
        '''
        eSrc, eTrg = self.check_src_and_trg_exist(src, trg)
        eSrc.includes.add({'trg': eTrg, 'guard': guard})

    def add_exclude(self, src, trg, guard=True):
        '''
        src -->% trg
        :return:
        '''
        eSrc, eTrg = self.check_src_and_trg_exist(src, trg)
        eSrc.excludes.add({'trg': eTrg, 'guard': guard})

    def execute(self, event):
        if self.has_event(event):
            self.get_event(event).execute()

    def is_accepting(self):
        for e in self.__events:
            if not e.is_accepting():
                return False
        return True

    def can_time_step(self, diff):
        for e in self.__events:
            if not e.can_time_step(diff):
                return False
        return True

    def time_step(self, diff):
        for e in self.__events:
            e.time_step(diff)

    def status(self):
        res = []
        for e in self.__events:
            res.append({'executed': e.marking.executed,
                        'pending': e.marking.pending,
                        'included': e.marking.included,
                        'enabled': e.enabled(),
                        'name': e.name,
                        'lastExecuted': e.marking.last_executed,
                        'deadline': e.marking.deadline,
                        'label': e.label
                        })
            for s in e.children.status():
                s['label'] = f'{e.label}.{s.label}'
                res.append(s)

        return res

class DCRGraphSubprocess(DCRGraph):
    def __init__(self, parent_graph: None) -> None:
        super().__init__(parent_graph)

class DCRGraphNesting(DCRGraphSubprocess):

    def __init__(self, parent_graph: None) -> None:
        super().__init__(parent_graph)


class DCRGraphSpawn(DCRGraph):
    def __init__(self, parent_graph: None) -> None:
        super().__init__(parent_graph)