from pm4py.objects import petri


def get_new_place(counts):
    """
    Create a new place in the Petri net
    """
    counts.inc_places()
    return petri.petrinet.PetriNet.Place('p_' + str(counts.num_places))


def get_new_hidden_trans(counts, type_trans="unknown"):
    """
    Create a new hidden transition in the Petri net
    """
    counts.inc_no_hidden()
    return petri.petrinet.PetriNet.Transition(type_trans + '_' + str(counts.num_hidden), None)


def get_transition(counts, label):
    """
    Create a transitions with the specified label in the Petri net
    """
    counts.inc_no_visible()
    return petri.petrinet.PetriNet.Transition(label, label)
