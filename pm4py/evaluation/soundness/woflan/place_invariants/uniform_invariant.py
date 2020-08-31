from pm4py.evaluation.soundness.woflan.place_invariants.place_invariants import compute_place_invariants
from pm4py.evaluation.soundness.woflan.place_invariants.utility import transform_basis

def apply(net):
    place_invariants= compute_place_invariants(net)
    modified_invariants=transform_basis(place_invariants, style='uniform')
    return modified_invariants

