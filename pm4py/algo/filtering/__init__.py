from pm4py.algo.filtering import log, common, dfg
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.algo.filtering import pandas
