from pm4py.statistics.concurrent_activities import log
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.statistics.concurrent_activities import pandas
