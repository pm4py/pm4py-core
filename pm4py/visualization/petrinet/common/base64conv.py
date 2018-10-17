import base64


def get_base64_from_gviz(gviz):
    """
    Get base 64 from string content of the file

    Parameters
    -----------
    gviz
        Graphviz diagram

    Returns
    -----------
    base64
        Base64 string
    """
    render = gviz.render(view=False)
    with open(render, "rb") as f:
        return base64.b64encode(f.read())
