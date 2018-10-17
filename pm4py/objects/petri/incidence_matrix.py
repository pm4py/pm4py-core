class IncidenceMatrix(object):

    def __init__(self, net):
        self.__A, self.__place_indices, self.__transition_indices = self.__construct_matrix(net)

    def encode_marking(self, marking):
        x = [0 for i in range(len(self.places))]
        for p in marking:
            x[self.places[p]] = marking[p]
        return x

    def __get_a_matrix(self):
        return self.__A

    def __get_transition_indices(self):
        return self.__transition_indices

    def __get_place_indices(self):
        return self.__place_indices

    def __construct_matrix(self, net):
        self.matrix_built = True
        p_index, t_index = {}, {}
        for p in net.places:
            p_index[p] = len(p_index)
        for t in net.transitions:
            t_index[t] = len(t_index)
        a_matrix = [[0 for i in range(len(t_index))] for j in range(len(p_index))]
        for p in net.places:
            for a in p.in_arcs:
                a_matrix[p_index[p]][t_index[a.source]] += 1
            for a in p.out_arcs:
                a_matrix[p_index[p]][t_index[a.target]] -= 1
        return a_matrix, p_index, t_index

    a_matrix = property(__get_a_matrix)
    places = property(__get_place_indices)
    transitions = property(__get_transition_indices)


def construct(net):
    return IncidenceMatrix(net)
