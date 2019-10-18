from pm4py.algo.simulation.montecarlo.versions import petri_arrival_time

PETRI_ARRIVAL_TIME = 'petri_arrival_time'

VERSIONS = {PETRI_ARRIVAL_TIME: petri_arrival_time.apply}

def apply(log, net, im, fm, variant=PETRI_ARRIVAL_TIME, parameters=None):
    return VERSIONS[variant](log, net, im, fm, parameters=parameters)
