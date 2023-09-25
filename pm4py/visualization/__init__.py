import importlib.util

if importlib.util.find_spec("graphviz"):
    # imports the visualizations only if graphviz is installed
    from pm4py.visualization import common, dfg, petri_net, process_tree, transition_system, \
        bpmn, trie, ocel, network_analysis
    if importlib.util.find_spec("matplotlib") and importlib.util.find_spec("pyvis"):
        # SNA requires both packages matplotlib and pyvis. These are included in the default installation;
        # however, they may lead to problems in some platforms/deployments
        from pm4py.visualization import sna, performance_spectrum
    if importlib.util.find_spec("pydotplus"):
        # heuristics net visualization requires pydotplus. This is included in the default installation;
        # however, they may lead to problems in some platforms/deployments
        from pm4py.visualization import heuristics_net

if importlib.util.find_spec("matplotlib"):
    # graphs require matplotlib. This is included in the default installation;
    # however, they may lead to problems in some platforms/deployments
    from pm4py.visualization import graphs
