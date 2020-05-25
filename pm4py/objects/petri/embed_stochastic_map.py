from pm4py.util.constants import STOCHASTIC_DISTRIBUTION


def apply(smap, parameters=None):
    """
    Embed the stochastic map into the Petri net

    Parameters
    ---------------
    smap
        Stochastic map
    parameters
        Possible parameters of the algorithm

    Returns
    ---------------
    void
    """
    if parameters is None:
        parameters = {}

    for t in smap:
        t.properties[STOCHASTIC_DISTRIBUTION] = smap[t]


def extract(net, parameters=None):
    """
    Extract the stochastic map from the Petri net

    Parameters
    --------------
    net
        Petri net
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    void
    """
    if parameters is None:
        parameters = {}

    smap = {}

    for t in net.transitions:
        smap[t] = t.properties[STOCHASTIC_DISTRIBUTION]

    return smap
