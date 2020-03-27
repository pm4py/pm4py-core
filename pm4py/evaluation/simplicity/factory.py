import deprecation

from pm4py.evaluation.simplicity.versions import arc_degree

SIMPLICITY_ARC_DEGREE = "arc_degree"
VERSIONS = {SIMPLICITY_ARC_DEGREE: arc_degree.apply}

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use evaluator entrypoint instead')
def apply(petri_net, parameters=None, variant="arc_degree"):
    return VERSIONS[variant](petri_net, parameters=parameters)
