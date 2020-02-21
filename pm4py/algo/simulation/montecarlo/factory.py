from pm4py.algo.simulation.montecarlo.versions import petri_semaph_fifo

PETRI_SEMAPH_FIFO = 'petri_semaph_fifo'

DEFAULT_VARIANT = PETRI_SEMAPH_FIFO

VERSIONS = {PETRI_SEMAPH_FIFO: petri_semaph_fifo.apply}


def apply(log, net, im, fm, variant=PETRI_SEMAPH_FIFO, parameters=None):
    """
    Performs a Monte Carlo simulation of the Petri net

    Parameters
    -------------
    log
        Event log
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    variant
        Variant of the algorithm to use
    parameters
        Parameters of the algorithm

    Returns
    ------------
    simulated_log
        Simulated event log
    simulation_result
        Result of the simulation
    """
    return VERSIONS[variant](log, net, im, fm, parameters=parameters)
