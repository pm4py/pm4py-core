from pm4py.algo.simulation.playout.versions import basic_playout

BASIC_PLAYOUT = "basic_playout"
VERSIONS = {BASIC_PLAYOUT: basic_playout.apply}


def apply(net, initial_marking, parameters=None, variant=BASIC_PLAYOUT):
    """
    Do the playout of a Petrinet generating a log

    Parameters
    -----------
    net
        Petri net to play-out
    initial_marking
        Initial marking of the Petri net
    parameters
        Parameters of the algorithm:
            noTraces -> Number of traces of the log to generate
            maxTraceLength -> Maximum trace length
    variant
        Variant of the algorithm to use
    """
    return VERSIONS[variant](net, initial_marking, parameters=parameters)
