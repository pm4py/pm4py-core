from pm4py.simulation.tree_generator.versions import basic, ptandloggenerator
import deprecation

BASIC = "basic"
PTANDLOGGENERATOR = "ptandloggenerator"

VERSIONS = {BASIC: basic.apply, PTANDLOGGENERATOR: ptandloggenerator.apply}

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use simulator module instead.')
def apply(variant=PTANDLOGGENERATOR, parameters=None):
    """
    Generate a process tree

    Parameters
    ------------
    variant
        Variant of the algorithm. Admitted values: basic
    parameters
        Paramters of the algorithm, including:
            rec_depth -> current recursion depth
            min_rec_depth -> minimum recursion depth
            max_rec_depth -> maximum recursion depth
            prob_leaf -> Probability to get a leaf

    Returns
    ------------
    tree
        Process tree
    """
    return VERSIONS[variant](parameters=parameters)
