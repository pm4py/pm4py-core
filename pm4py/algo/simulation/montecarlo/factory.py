from pm4py.algo.simulation.montecarlo.versions import petri_arrival_time_max_1t

PETRI_ARRIVAL_TIME_MAX_1T = 'petri_arrival_time_max_1t'

VERSIONS = {PETRI_ARRIVAL_TIME_MAX_1T: petri_arrival_time_max_1t.apply}

def apply(log, net, im, fm, variant=PETRI_ARRIVAL_TIME_MAX_1T, parameters=None):
    return VERSIONS[variant](log, net, im, fm, parameters=parameters)
