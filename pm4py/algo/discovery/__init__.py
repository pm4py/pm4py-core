from pm4py.algo.discovery import dfg, alpha, inductive, transition_system, log_skeleton, footprints, minimum_self_distance
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.algo.discovery import correlation_mining
