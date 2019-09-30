from pm4py.algo.simulation.tree_generator.versions import basic, ptandloggenerator

BASIC = "basic"
PTANDLOGGENERATOR = "ptandloggenerator"

VERSIONS = {BASIC: basic.apply, PTANDLOGGENERATOR: ptandloggenerator.apply}


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
