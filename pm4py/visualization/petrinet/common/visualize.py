import tempfile

from graphviz import Digraph

from pm4py.objects.petri.petrinet import Marking

FORMAT = "format"
DEBUG = "debug"
RANKDIR = "set_rankdir"


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
    set_rankdir = None
    if FORMAT in parameters:
        image_format = parameters["format"]
    if DEBUG in parameters:
        debug = parameters["debug"]
    if RANKDIR in parameters:
        set_rankdir = parameters[RANKDIR]
    return graphviz_visualization(net, image_format=image_format, initial_marking=initial_marking,
                                  final_marking=final_marking, decorations=decorations, debug=debug,
                                  set_rankdir=set_rankdir)


def graphviz_visualization(net, image_format="png", initial_marking=None, final_marking=None, decorations=None,
                           debug=False, set_rankdir=None):
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
    set_rankdir
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
    viz = Digraph(net.name, filename=filename.name, engine='dot', graph_attr={'bgcolor': 'transparent'})
    if set_rankdir:
        viz.graph_attr['rankdir'] = set_rankdir
    else:
        viz.graph_attr['rankdir'] = 'LR'

    # transitions
    viz.attr('node', shape='box')
    # add transitions, in order by their (unique) name, to avoid undeterminism in the visualization
    trans_sort_list = sorted(list(net.transitions), key=lambda x: (x.label if x.label is not None else "tau", x.name))
    for t in trans_sort_list:
        if t.label is not None:
            if t in decorations and "label" in decorations[t] and "color" in decorations[t]:
                viz.node(str(id(t)), decorations[t]["label"], style='filled', fillcolor=decorations[t]["color"],
                         border='1')
            else:
                viz.node(str(id(t)), str(t.label))
        else:
            if debug:
                viz.node(str(id(t)), str(t.name))
            else:
                viz.node(str(id(t)), "", style='filled', fillcolor="black")

    # places
    viz.attr('node', shape='circle', fixedsize='true', width='0.75')
    # add places, in order by their (unique) name, to avoid undeterminism in the visualization
    places_sort_list_im = sorted([x for x in list(net.places) if x in initial_marking], key=lambda x: x.name)
    places_sort_list_fm = sorted([x for x in list(net.places) if x in final_marking and not x in initial_marking],
                                 key=lambda x: x.name)
    places_sort_list_not_im_fm = sorted(
        [x for x in list(net.places) if x not in initial_marking and x not in final_marking], key=lambda x: x.name)
    # making the addition happen in this order:
    # - first, the places belonging to the initial marking
    # - after, the places not belonging neither to the initial marking and the final marking
    # - at last, the places belonging to the final marking (but not to the initial marking)
    # in this way, is more probable that the initial marking is on the left and the final on the right
    places_sort_list = places_sort_list_im + places_sort_list_not_im_fm + places_sort_list_fm

    for p in places_sort_list:
        if p in initial_marking:
            viz.node(str(id(p)), str(initial_marking[p]), style='filled', fillcolor="green")
        elif p in final_marking:
            viz.node(str(id(p)), "", style='filled', fillcolor="orange")
        else:
            if debug:
                viz.node(str(id(p)), str(p.name))
            else:
                viz.node(str(id(p)), "")

    # add arcs, in order by their source and target objects names, to avoid undeterminism in the visualization
    arcs_sort_list = sorted(list(net.arcs), key=lambda x: (x.source.name, x.target.name))
    for a in arcs_sort_list:
        if a in decorations:
            viz.edge(str(id(a.source)), str(id(a.target)), label=decorations[a]["label"],
                     penwidth=decorations[a]["penwidth"])
        else:
            viz.edge(str(id(a.source)), str(id(a.target)))
    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = image_format

    return viz
