from pm4py.algo.discovery.footprints.outputs import Outputs


def apply(dfg, parameters=None):
    """
    Discovers a footprint object from a DFG

    Parameters
    --------------
    dfg
        DFG
    parameters
        Parameters of the algorithm

    Returns
    --------------
    footprints_obj
        Footprints object
    """
    if parameters is None:
        parameters = {}

    parallel = {(x, y) for (x, y) in dfg if (y, x) in dfg}
    sequence = {(x, y) for (x, y) in dfg if not (y, x) in dfg}

    return {Outputs.SEQUENCE.value: sequence, Outputs.PARALLEL.value: parallel}
