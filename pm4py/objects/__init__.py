from pm4py.objects import log, petri_net, transition_system, conversion, process_tree, \
    dfg, trie, org
import pkgutil

if pkgutil.find_loader("networkx"):
    from pm4py.objects import bpmn
