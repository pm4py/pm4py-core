from pm4py.visualization.petrinet.versions import wo_decoration, token_decoration, greedy_decoration
import os, shutil
from pm4py.visualization.common.save import *
from pm4py.visualization.common.gview import *

WO_DECORATION = "wo_decoration"
FREQUENCY_DECORATION = "frequency"
PERFORMANCE_DECORATION = "performance"
FREQUENCY_GREEDY = "frequency_greedy"
PERFORMANCE_GREEDY = "performance_greedy"

VERSIONS = {WO_DECORATION: wo_decoration.apply, FREQUENCY_DECORATION:token_decoration.apply_frequency,
            PERFORMANCE_DECORATION:token_decoration.apply_performance, FREQUENCY_GREEDY:greedy_decoration.apply_frequency,
            PERFORMANCE_GREEDY:greedy_decoration.apply_performance}

def apply(net, initial_marking, final_marking, log=None, aggregated_statistics=None, parameters=None, variant="wo_decoration"):
    return VERSIONS[variant](net, initial_marking, final_marking, log=log, aggregated_statistics=aggregated_statistics, parameters=parameters)