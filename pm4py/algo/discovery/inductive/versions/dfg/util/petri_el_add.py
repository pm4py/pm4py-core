from pm4py.entities import petri

def get_new_place(counts):
    """
    Create a new place in the Petri net
    """
    counts.inc_places()
    return petri.petrinet.PetriNet.Place('p_' + str(counts.num_places))


def get_new_hidden_trans(counts, type="unknown"):
    """
    Create a new hidden transition in the Petri net
    """
    counts.inc_noOfHidden()
    return petri.petrinet.PetriNet.Transition(type + '_' + str(counts.num_hidden), None)


def get_transition(counts, label):
    """
    Create a transitions with the specified label in the Petri net
    """
    counts.inc_noOfVisible()
    return petri.petrinet.PetriNet.Transition(label, label)