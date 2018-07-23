
class PetriNet(object):
    class Place(object):

        def __init__(self, name):
            self.__name = name

        def __set_name(self, name):
            self.__name = name

        def __get_name(self):
            return self.__name

        name = property(__get_name, __set_name)

    class Transition(object):

        def __init__(self, name, label=None):
            self.__name = name
            self.__label = label

        def __set_name(self, name):
            self.__name = name

        def __get_name(self):
            return self.__name

        def __set_label(self, label):
            self.__label = label

        def __get_label(self):
            return self.__label

        name = property(__get_name, __set_name)
        label = property(__get_label, __set_label)

    class Arc(object):

        def __init__(self, source, target, weight=1):
            if type(source) is type(target):
                raise Exception('Petri nets are bipartite!')
            self.__source = source
            self.__target = target
            self.__wight = weight

        def __get_source(self):
            return self.__source

        def __get_target(self):
            return self.__target

        def __set_weight(self, weight):
            self.__wight = weight

        def __get_weight(self):
            return self.__weight

        source = property(__get_source)
        target = property(__get_target)
        weight = property(__get_weight, __set_weight)

    def __init__(self, name="", places=None, transitions=None, arcs=None):
        self.__name = name
        if places is None:
            self.__places = set()
        else:
            self.__places = places
        if transitions is None:
            self.__transitions = set()
        else:
            self.__transitions = transitions
        if arcs is None:
            self.__arcs = set()
        else:
            self.__arcs = arcs

    def __get_name(self):
        return self.__name

    def __set_name(self, name):
        self.__name = name

    def __get_places(self):
        return self.__places

    def __get_transitions(self):
        return self.__transitions

    def __get_arcs(self):
        return self.__arcs

    name = property(__get_name, __set_name)
    places = property(__get_places)
    transitions = property(__get_transitions)
    arcs = property(__get_arcs)



