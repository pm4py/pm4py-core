def view(gviz):
    is_ipynb = False

    try:
        get_ipython()
        is_ipynb = True
    except:
        pass

    if is_ipynb:
        from IPython.display import Image
        return Image(open(gviz.render(), "rb").read())
    else:
        return gviz.view()