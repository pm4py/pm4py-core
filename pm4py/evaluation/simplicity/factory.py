from pm4py.evaluation.simplicity.versions import arc_degree

SIMPLICITY_ARC_DEGREE = "arc_degree"
VERSIONS = {SIMPLICITY_ARC_DEGREE: arc_degree.apply}


def apply(petri_net, parameters=None, variant="arc_degree"):
    return VERSIONS[variant](petri_net, parameters=parameters)
