import tempfile

from pm4py.util import vis_utils


def view(gviz):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    if vis_utils.check_visualization_inside_jupyter():
        vis_utils.view_image_in_jupyter(gviz.render())
    else:
        return gviz.view(cleanup=True)


def matplotlib_view(gviz):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    from pm4py.visualization.common import save
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    file_name = tempfile.NamedTemporaryFile(suffix='.png')
    file_name.close()

    save.save(gviz, file_name.name)

    img = mpimg.imread(file_name.name)
    plt.imshow(img)
    plt.show()
