from pm4py.algo.discovery import alpha, dfg, heuristics, inductive, transition_system, log_skeleton, footprints, temporal_profile
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.algo.discovery import correlation_mining
