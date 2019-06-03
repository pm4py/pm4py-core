import tempfile

from graphviz import Digraph

from pm4py.objects.petri.petrinet import Marking

FORMAT = "format"
DEBUG = "debug"
RANKDIR_LR = "set_rankdir_lr"


def apply(net, initial_marking, final_marking, decorations=None, parameters=None):
    """
    Apply method for Petri net visualization (useful for recall from factory; it calls the
    graphviz_visualization method)

    Parameters
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    decorations
        Decorations for elements in the Petri net
    parameters
        Algorithm parameters

    Returns
    -----------
    viz
        Graph object
    """
    if parameters is None:
        parameters = {}
    image_format = "png"
    debug = False
    set_rankdir_lr = False
    if FORMAT in parameters:
        image_format = parameters["format"]
    if DEBUG in parameters:
        debug = parameters["debug"]
    if RANKDIR_LR in parameters:
        set_rankdir_lr = parameters[RANKDIR_LR]
    return graphviz_visualization(net, image_format=image_format, initial_marking=initial_marking,
                                  final_marking=final_marking, decorations=decorations, debug=debug,
                                  set_rankdir_lr=set_rankdir_lr)


def graphviz_visualization(net, image_format="png", initial_marking=None, final_marking=None, decorations=None,
                           debug=False, set_rankdir_lr=False):
    """
    Provides visualization for the petrinet

    Parameters
    ----------
    net: :class:`pm4py.entities.petri.petrinet.PetriNet`
        Petri net
    image_format
        Format that should be associated to the image
    initial_marking
        Initial marking of the Petri net
    final_marking
        Final marking of the Petri net
    decorations
        Decorations of the Petri net (says how element must be presented)
    debug
        Enables debug mode
    set_rankdir_lr
        Sets the rankdir to LR (horizontal layout)

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
    viz = Digraph(net.name, filename=filename.name, engine='dot', graph_attr={'bgcolor':'transparent'})
    if set_rankdir_lr:
        viz.graph_attr['rankdir'] = 'LR'

    # transitions
    viz.attr('node', shape='box')
    for t in net.transitions:
        if t.label is not None:
            if t in decorations and "label" in decorations[t] and "color" in decorations[t]:
                viz.node(str(hash(t.name)), decorations[t]["label"], style='filled', fillcolor=decorations[t]["color"],
                         border='1')
            else:
                viz.node(str(hash(t.name)), str(t.label))
        else:
            if debug:
                viz.node(str(hash(t.name)), str(t.name))
            else:
                viz.node(str(hash(t.name)), "", style='filled', fillcolor="black")

    # places
    viz.attr('node', shape='circle', fixedsize='true', width='0.75')
    for p in net.places:
        if p in initial_marking:
            viz.node(str(hash(p.name)), str(initial_marking[p]), style='filled', fillcolor="green")
        elif p in final_marking:
            viz.node(str(hash(p.name)), "", style='filled', fillcolor="orange")
        else:
            if debug:
                viz.node(str(hash(p.name)), str(p.name))
            else:
                viz.node(str(hash(p.name)), "")

    # arcs
    for a in net.arcs:
        if a in decorations:
            viz.edge(str(hash(a.source.name)), str(hash(a.target.name)), label=decorations[a]["label"],
                     penwidth=decorations[a]["penwidth"])
        else:
            viz.edge(str(hash(a.source.name)), str(hash(a.target.name)))
    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = image_format

    return viz
