def view(gviz):
    is_ipynb = False

    try:
        get_ipython()
        is_ipynb = True
    except:
        pass

    if is_ipynb:
        return Image(open(gviz.render(), "rb").read())
    else:
        return gviz.view()