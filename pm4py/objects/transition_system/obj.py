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
from pm4py.objects.transition_system import constants


class TransitionSystem(object):
    class State(object):
        def __init__(self, name, incoming=None, outgoing=None, data=None):
            self.__name = name
            self.__incoming = set() if incoming is None else incoming
            self.__outgoing = set() if outgoing is None else outgoing
            self.__data = {constants.INGOING_EVENTS: [], constants.OUTGOING_EVENTS: []} if data is None else data

        def __get_name(self):
            return self.__name

        def __set_name(self, name):
            self.__name = name

        def __get_outgoing(self):
            return self.__outgoing

        def __set_outgoing(self, outgoing):
            self.__outgoing = outgoing

        def __get_incoming(self):
            return self.__incoming

        def __set_incoming(self, incoming):
            self.__incoming = incoming

        def __get_data(self):
            return self.__data

        def __set_data(self, data):
            self.__data = data

        def __repr__(self):
            return str(self.name)

        name = property(__get_name, __set_name)
        incoming = property(__get_incoming, __set_incoming)
        outgoing = property(__get_outgoing, __set_outgoing)
        data = property(__get_data, __set_data)

    class Transition(object):

        def __init__(self, name, from_state, to_state, data=None):
            self.__name = name
            self.__from_state = from_state
            self.__to_state = to_state
            self.__data = {constants.EVENTS: []} if data is None else data

        def __get_name(self):
            return self.__name

        def __get_to_state(self):
            return self.__to_state

        def __set_to_state(self, to_state):
            self.__to_state = to_state

        def __get_from_state(self):
            return self.__from_state

        def __set_from_state(self, from_state):
            self.__from_state = from_state

        def __get_data(self):
            return self.__data

        def __set_data(self, data):
            self.__data = data

        def __repr__(self):
            return str(self.name)

        name = property(__get_name)
        from_state = property(__get_from_state, __set_from_state)
        to_state = property(__get_to_state, __set_to_state)
        data = property(__get_data, __set_data)

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

    def __set_transitions(self, transitions):
        self.__transitions = transitions

    name = property(__get_name, __set_name)
    states = property(__get_states)
    transitions = property(__get_transitions, __set_transitions)
