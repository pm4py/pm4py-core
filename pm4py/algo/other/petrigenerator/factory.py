from pm4py.algo.other.petrigenerator.versions import simple_generator

SIMPLE_GENERATOR = "simple_generator"
VERSIONS = {SIMPLE_GENERATOR: simple_generator}

def apply(parameters=None, variant="SIMPLE_GENERATOR"):
    """
    Generate a Petri net

    Parameters
    ----------
    parameters
        Parameters for the algorithm:
         minNoOfActivitiesPerSubtree -> Minimum number of attributes per distinct subtree
        maxNoOfActivitiesPerSubtree -> Maximum number of attributes per distinct subtree
        maxNoOfSubtrees -> Maximum number of subtrees that should be added to the Petri net
        probSpawnSubtree -> Probability of spawn of a new subtree
        probAutoSkip -> Probability of adding a hidden transition that skips the current subtree
        probAutoLoop -> Probability of adding a hidden transition that loops on the current subtree
        possible_behaviors -> Possible behaviors admitted (sequential, concurrent, parallel, flower)
    """
    return VERSIONS[variant](parameters)