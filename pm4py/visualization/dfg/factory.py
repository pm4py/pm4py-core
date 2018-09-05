from pm4py.visualization.dfg.versions import simple_visualize
import os, shutil

FREQUENCY = "frequency"
PERFORMANCE = "performance"

VERSIONS = {FREQUENCY: simple_visualize.apply_frequency, PERFORMANCE: simple_visualize.apply_performance}

def apply(dfg, log=None, activities_count=None, parameters=None, variant="frequency"):
    return VERSIONS[variant](dfg, log=log, activities_count=activities_count, parameters=parameters)

def save(gviz, outputFilePath):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    outputFilePath
        Path where the GraphViz output should be saved
    """
    render = gviz.render()
    shutil.copyfile(render, outputFilePath)