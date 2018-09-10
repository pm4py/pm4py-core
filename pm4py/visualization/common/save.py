import os, shutil

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