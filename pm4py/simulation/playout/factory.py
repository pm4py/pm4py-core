from pm4py.simulation.playout.versions import basic_playout
import deprecation

BASIC_PLAYOUT = "basic_playout"
VERSIONS = {BASIC_PLAYOUT: basic_playout.apply}


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use simulator module instead.')
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
