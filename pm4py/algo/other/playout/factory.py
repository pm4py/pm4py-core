from pm4py.algo.other.playout.versions import basic_playout

BASIC_PLAYOUT = "basic_playout"
VERSIONS = {BASIC_PLAYOUT: basic_playout.apply}

def apply(net, initialMarking, parameters=None, variant="basic_playout"):
    """
    Do the playout of a Petrinet generating a log

    Parameters
    -----------
    net
        Petri net to play-out
    parameters
        Parameters of the algorithm

    Parameters:
        noTraces -> Number of traces of the log to generate
        maxTraceLength -> Maximum trace length
    """
    return VERSIONS[variant](net, initialMarking)