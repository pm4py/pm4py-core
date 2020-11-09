from pm4py.statistics.passed_time import log
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.statistics.passed_time import pandas

