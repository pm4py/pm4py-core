from pm4py.algo.discovery.temporal_profile.variants import log
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.algo.discovery.temporal_profile.variants import dataframe
