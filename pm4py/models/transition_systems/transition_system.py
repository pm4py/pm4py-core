class TransitionSystem(object):

    class State(object):
        def __init__(self, name, incoming=None, outgoing=None):
            self.__name = name
            self.__incoming = set() if incoming is None else incoming
            self.__outgoing = set() if outgoing is None else outgoing

        def __set_name(self, name):
            self.__name = name

        def __get_name(self):
            return self.__name

        def __get_outgoing(self):
            return self.__outgoing

        def __get_incoming(self):
            return self.__incoming

        def __repr__(self):
            return str(self.name)

        name = property(__get_name, __set_name)
        incoming = property(__get_incoming)
        outgoing = property(__get_outgoing)

    class Transition(object):

        def __init__(self, name, from_state=None, to_state=None):
            self.__name = name
            self.__from_state = set() if from_state is None else from_state
            self.__to_state = set() if to_state is None else to_state

        def __set_name(self, name):
            self.__name = name

        def __get_name(self):
            return self.__name

        def __get_out_arcs(self):
            return self.__to_state

        def __get_in_arcs(self):
            return self.__from_state

        def __repr__(self):
            return str(self.name)

        name = property(__get_name, __set_name)
        in_arcs = property(__get_in_arcs)
        out_arcs = property(__get_out_arcs)

    def __init__(self, name=None, states=None, transitions=None):
        self.__name = "" if name is None else name
        self.__states = set() if states is None else states
        self.__transitions = set() if transitions is None else transitions

    def __get_name(self):
        return self.__name

    def __set_name(self, name):
        self.__name = name

    def __get_states(self):
        return self.__states

    def __get_transitions(self):
        return self.__transitions

    name = property(__get_name, __set_name)
    places = property(__get_states)
    transitions = property(__get_transitions)

