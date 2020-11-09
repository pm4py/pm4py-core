from pm4py.statistics.sojourn_time import log
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.statistics.sojourn_time import pandas
