from graphviz import Digraph
import tempfile, os
import base64

def graphviz_visualization(net, format="pdf"):
    """
    Provides visualization for the petrinet

    Parameters
    ----------
    net: :class:`pm4py.models.petri.petrinet.PetriNet`
        Petri net

    Returns
    -------
    viz :
        Returns a graph object
    """
    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph(net.name, filename=filename.name, engine='dot')

    #transitions
    viz.attr('node', shape='box')
    for t in net.transitions:
        if t.label is not None:
            viz.node(str(t.name), str(t.label))
        else:
            viz.node(str(t.name), str(t.name))

    #places
    viz.attr('node', shape='circle', fixedsize='true', width='0.75')
    for p in net.places:
        viz.node(str(p.name))

    #arcs
    for a in net.arcs:
        viz.edge(str(a.source.name), str(a.target.name))

    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = format

    return viz

def return_diagram_as_base64(net, format="svg"):
    """
    Return process model in Base64 format

    Parameters
    -----------
    net: :class:`pm4py.models.petri.petrinet.PetriNet`
        Petri net

    Returns
    -----------
    string
        Base 64 string representing the model in the provided format
    """
    graphviz = graphviz_visualization(net, format=format)
    render = graphviz.render(view=False)
    with open(render, "rb") as f:
        return base64.b64encode(f.read())