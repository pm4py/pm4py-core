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
        image = Image(open(gviz.render(), "rb").read())
        from IPython.display import display
        return display(image)
    else:
        return gviz.view()
