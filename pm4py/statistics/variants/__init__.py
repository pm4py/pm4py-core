from pm4py.statistics.variants import log
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.statistics.variants import pandas
