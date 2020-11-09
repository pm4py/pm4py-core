from pm4py.algo.discovery.dfg import algorithm, replacement, variants, utils
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.algo.discovery.dfg import adapters

