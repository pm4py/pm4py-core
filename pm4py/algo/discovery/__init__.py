from pm4py.algo.discovery import dfg, alpha, heuristics, inductive, transition_system, log_skeleton, footprints, temporal_profile, minimum_self_distance
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.algo.discovery import correlation_mining
