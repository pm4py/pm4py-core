import shutil


def save(gviz, output_file_path):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    render = gviz.render(cleanup=True)
    shutil.copyfile(render, output_file_path)
