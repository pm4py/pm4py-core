from pm4py.algo.conformance.alignments import decomposed, dfg, petri_net, process_tree
import pkgutil

if pkgutil.find_loader("stringdist"):
    from pm4py.algo.conformance.alignments import edit_distance
