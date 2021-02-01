from pm4py.algo.conformance.temporal_profile.variants import log
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.algo.conformance.temporal_profile.variants import dataframe
