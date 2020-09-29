import tempfile


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
