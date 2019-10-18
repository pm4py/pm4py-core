from pm4py.algo.simulation.montecarlo.versions import petri_arrival_time_max_1t

PETRI_ARRIVAL_TIME_MAX_1T = 'petri_arrival_time_max_1t'

VERSIONS = {PETRI_ARRIVAL_TIME_MAX_1T: petri_arrival_time_max_1t.apply}


def apply(log, net, im, fm, variant=PETRI_ARRIVAL_TIME_MAX_1T, parameters=None):
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
