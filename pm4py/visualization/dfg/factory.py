from pm4py.visualization.dfg.versions import simple_visualize
import os, shutil
from pm4py.visualization.common.save import *
from pm4py.visualization.common.gview import *

FREQUENCY = "frequency"
PERFORMANCE = "performance"
FREQUENCY_GREEDY = "frequency_greedy"
PERFORMANCE_GREEDY = "performance_greedy"

VERSIONS = {FREQUENCY: simple_visualize.apply_frequency, PERFORMANCE: simple_visualize.apply_performance,
            FREQUENCY_GREEDY: simple_visualize.apply_frequency, PERFORMANCE_GREEDY: simple_visualize.apply_performance}

def apply(dfg, log=None, activities_count=None, parameters=None, variant="frequency"):
    return VERSIONS[variant](dfg, log=log, activities_count=activities_count, parameters=parameters)