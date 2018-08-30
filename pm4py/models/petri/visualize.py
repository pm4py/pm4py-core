from graphviz import Digraph
import tempfile, os
import base64
from pm4py.models.petri.petrinet import Marking
from random import random

def graphviz_visualization(net, format="pdf", initial_marking=None, final_marking=None, decorations=None, debug=False):
    """
    Provides visualization for the petrinet

    Parameters
    ----------
    net: :class:`pm4py.models.petri.petrinet.PetriNet`
        Petri net
    initial_marking
        Initial marking of the Petri net
    final_marking
        Final marking of the Petri net
    decorations
        Decorations of the Petri net (says how element must be presented)
    debug
        Enables debug mode

    Returns
    -------
    viz :
        Returns a graph object
    """
    if initial_marking is None:
        initial_marking = Marking()
    if final_marking is None:
        final_marking = Marking()
    if decorations is None:
        decorations = {}

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph(net.name, filename=filename.name, engine='dot')

    #transitions
    viz.attr('node', shape='box')
    for t in net.transitions:
        if t.label is not None:
            if t in decorations:
                viz.node(str(t.name), decorations[t]["label"], style='filled', fillcolor=decorations[t]["color"], border='1')
            else:
                viz.node(str(t.name), str(t.label))
        else:
            if debug:
                viz.node(str(t.name), str(t.name))
            else:
                viz.node(str(t.name), "", style='filled', fillcolor="black")

    #places
    viz.attr('node', shape='circle', fixedsize='true', width='0.75')
    for p in net.places:
        if p in initial_marking:
            viz.node(str(p.name), str(initial_marking[p]), style='filled', fillcolor="green")
        elif p in final_marking:
            viz.node(str(p.name), "", style='filled', fillcolor="orange")
        else:
            if debug:
                viz.node(str(p.name), str(p.name))
            else:
                viz.node(str(p.name), "")


    #arcs
    for a in net.arcs:
        if a in decorations:
            viz.edge(str(a.source.name), str(a.target.name), label=decorations[a]["label"], penwidth=decorations[a]["penwidth"])
        else:
            viz.edge(str(a.source.name), str(a.target.name))
    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = format

    return viz

def return_diagram_as_base64(net, format="svg", initial_marking=None, final_marking=None, decorations=None, debug=False):
    """
    Return process model in Base64 format

    Parameters
    -----------
    net: :class:`pm4py.models.petri.petrinet.PetriNet`
        Petri net
    initial_marking
        Initial marking of the Petri net
    final_marking
        Final marking of the Petri net
    decorations
        Decorations of the Petri net (says how element must be presented)

    Returns
    -----------
    string
        Base 64 string representing the model in the provided format
    """
    graphviz = graphviz_visualization(net, format=format, initial_marking=initial_marking, final_marking=final_marking, decorations=decorations, debug=debug)
    render = graphviz.render(view=False)
    with open(render, "rb") as f:
        return base64.b64encode(f.read())