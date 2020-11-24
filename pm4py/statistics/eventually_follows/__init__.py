from pm4py.statistics.eventually_follows import log
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.statistics.eventually_follows import pandas
