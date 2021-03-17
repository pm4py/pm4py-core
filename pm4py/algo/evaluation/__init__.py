from pm4py.algo.evaluation import precision
import pkgutil

if pkgutil.find_loader("pyemd"):
    # import the EMD only if the pyemd package is installed
    pass

if pkgutil.find_loader("networkx") and pkgutil.find_loader("sympy"):
    # import the Woflan package only if NetworkX and sympy are installed
    pass
