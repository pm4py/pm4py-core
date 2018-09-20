from pm4py.algo.conformance.tokenreplay.versions import token_replay

TOKEN_REPLAY = "token_replay"
VERSIONS = {TOKEN_REPLAY: token_replay.apply}

def apply(log, net, initialMarking, finalMarking, parameters=None, variant="token_replay"):
    """
    Factory method to apply token-based replay
    
    Parameters
    -----------
    log
        Log
    net
        Petri net
    initialMarking
        Initial marking
    finalMarking
        Final marking
    parameters
        Parameters of the algorithm
    activity_key
        Activity key (must be specified by the algorithm)
    variant
        Variant of the algorithm to use
    """
    return VERSIONS[variant](log, net, initialMarking, finalMarking, parameters=parameters)