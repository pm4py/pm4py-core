from pm4py.statistics.traces import log, common
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.statistics.traces import pandas
