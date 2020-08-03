import deprecation

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use visualizer module instead.')
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
