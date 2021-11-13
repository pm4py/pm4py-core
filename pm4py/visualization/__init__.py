import pkgutil

if pkgutil.find_loader("graphviz"):
    # imports the visualizations only if graphviz is installed
    from pm4py.visualization import common, dfg, petri_net, process_tree, transition_system, align_table, \
        footprints, bpmn, trie, dotted_chart, ocel
    if pkgutil.find_loader("matplotlib") and pkgutil.find_loader("pyvis"):
        # SNA requires both packages matplotlib and pyvis. These are included in the default installation;
        # however, they may lead to problems in some platforms/deployments
        from pm4py.visualization import sna, performance_spectrum
    if pkgutil.find_loader("pydotplus"):
        # heuristics net visualization requires pydotplus. This is included in the default installation;
        # however, they may lead to problems in some platforms/deployments
        from pm4py.visualization import heuristics_net
    if pkgutil.find_loader("sklearn"):
        from pm4py.visualization import decisiontree

if pkgutil.find_loader("matplotlib"):
    # graphs require matplotlib. This is included in the default installation;
    # however, they may lead to problems in some platforms/deployments
    from pm4py.visualization import graphs
