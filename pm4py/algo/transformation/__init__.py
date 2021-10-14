from pm4py.algo.transformation import log_to_trie, log_to_features
import pkgutil
if pkgutil.find_loader("intervaltree"):
    from pm4py.algo.transformation import log_to_interval_tree
