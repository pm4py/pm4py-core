from pm4py.objects import log, petri_net, transition_system, conversion, process_tree, \
    dfg, trie
import pkgutil

if pkgutil.find_loader("networkx"):
    from pm4py.objects import bpmn
