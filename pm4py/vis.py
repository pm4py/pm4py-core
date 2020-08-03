def view_petri_net(petri_net, format="png"):
    """
    Views a (composite) Petri net

    Parameters
    -------------
    petri_net
        Petri net
    format
        Format of the output picture (default: png)
    """
    net, im, fm = petri_net
    from pm4py.visualization.petrinet import visualizer as pn_visualizer
    gviz = pn_visualizer.apply(net, im, fm,
                               parameters={pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: format})
    pn_visualizer.view(gviz)


def save_vis_petri_net(petri_net, file_path):
    """
    Saves a Petri net visualization to a file

    Parameters
    --------------
    petri_net
        Petri net
    file_path
        Destination path
    """
    net, im, fm = petri_net
    format = file_path[file_path.index(".") + 1:].lower()
    from pm4py.visualization.petrinet import visualizer as pn_visualizer
    gviz = pn_visualizer.apply(net, im, fm,
                               parameters={pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: format})
    pn_visualizer.save(gviz, file_path)


def view_dfg(dfg, format="png", log=None):
    """
    Views a (composite) DFG

    Parameters
    -------------
    dfg
        DFG object
    format
        Format of the output picture (default: png)
    """
    dfg, start_activities, end_activities = dfg
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    parameters = dfg_visualizer.Variants.FREQUENCY.value.Parameters
    gviz = dfg_visualizer.apply(dfg, log=log, variant=dfg_visualizer.Variants.FREQUENCY,
                                parameters={parameters.FORMAT: format,
                                            parameters.START_ACTIVITIES: start_activities,
                                            parameters.END_ACTIVITIES: end_activities})
    dfg_visualizer.view(gviz)


def save_vis_dfg(dfg, file_path, log=None):
    """
    Saves a DFG visualization to a file

    Parameters
    --------------
    dfg
        DFG object
    file_path
        Destination path
    """
    dfg, start_activities, end_activities = dfg
    format = file_path[file_path.index(".") + 1:].lower()
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    parameters = dfg_visualizer.Variants.FREQUENCY.value.Parameters
    gviz = dfg_visualizer.apply(dfg, log=log, variant=dfg_visualizer.Variants.FREQUENCY,
                                parameters={parameters.FORMAT: format,
                                            parameters.START_ACTIVITIES: start_activities,
                                            parameters.END_ACTIVITIES: end_activities})
    dfg_visualizer.save(gviz, file_path)


def view_process_tree(tree, format="png"):
    """
    Views a process tree

    Parameters
    ---------------
    tree
        Process tree
    format
        Format of the visualization (default: png)
    """
    from pm4py.visualization.process_tree import visualizer as pt_visualizer
    parameters = pt_visualizer.Variants.WO_DECORATION.value.Parameters
    gviz = pt_visualizer.apply(tree, parameters={parameters.FORMAT: format})
    pt_visualizer.view(gviz)


def save_vis_process_tree(tree, file_path):
    """
    Saves the visualization of a process tree

    Parameters
    ---------------
    tree
        Process tree
    file_path
        Destination path
    """
    format = file_path[file_path.index(".") + 1:].lower()
    from pm4py.visualization.process_tree import visualizer as pt_visualizer
    parameters = pt_visualizer.Variants.WO_DECORATION.value.Parameters
    gviz = pt_visualizer.apply(tree, parameters={parameters.FORMAT: format})
    pt_visualizer.save(gviz, file_path)


def view_heuristics_net(heu_net, format="png"):
    """
    Views an heuristics net

    Parameters
    --------------
    heu_net
        Heuristics net
    format
        Format of the visualization (default: png)
    """
    from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
    parameters = hn_visualizer.Variants.PYDOTPLUS.value.Parameters
    gviz = hn_visualizer.apply(heu_net, parameters={parameters.FORMAT: format})
    hn_visualizer.view(gviz)


def save_vis_heuristics_net(heu_net, file_path):
    """
    Saves the visualization of an heuristics net

    Parameters
    --------------
    heu_net
        Heuristics nte
    file_path
        Destination path
    """
    format = file_path[file_path.index(".") + 1:].lower()
    from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
    parameters = hn_visualizer.Variants.PYDOTPLUS.value.Parameters
    gviz = hn_visualizer.apply(heu_net, parameters={parameters.FORMAT: format})
    hn_visualizer.save(gviz, file_path)
