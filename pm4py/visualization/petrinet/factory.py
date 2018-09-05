from pm4py.visualization.petrinet.versions import wo_decoration, token_decoration

WO_DECORATION = "wo_decoration"
FREQUENCY_DECORATION = "frequency"
PERFORMANCE_DECORATION = "performance"

VERSIONS = {WO_DECORATION: wo_decoration.apply, FREQUENCY_DECORATION:token_decoration.apply_frequency,
            PERFORMANCE_DECORATION:token_decoration.apply_performance}

def apply(net, initial_marking, final_marking, log=None, parameters=None, variant="wo_decoration"):
    return VERSIONS[variant](net, initial_marking, final_marking, log=log, parameters=parameters)