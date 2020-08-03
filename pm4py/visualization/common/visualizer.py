import shutil

from pm4py.util.vis_utils import human_readable_stat, get_arc_penwidth, get_trans_freq_color, get_base64_from_gviz, get_base64_from_file


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

def view(gviz):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    is_ipynb = False

    try:
        get_ipython()
        is_ipynb = True
    except NameError:
        # we are not inside Jupyter, do nothing
        pass

    if is_ipynb:
        from IPython.display import Image
        image = Image(gviz.render())
        from IPython.display import display
        return display(image)
    else:
        return gviz.view(cleanup=True)
